import llvmlite.ir as ir


i32 = ir.IntType(32)


def generate_empty_kernel() -> ir.Module:
    module = ir.Module()

    func_type = ir.FunctionType(
        return_type=ir.VoidType(),
        args=()
    )
    func_name = 'empty_kernel'
    func = ir.Function(
        module=module,
        ftype=func_type,
        name=func_name
    )

    entry_block = func.append_basic_block('entry')
    builder = ir.builder.IRBuilder(entry_block)
    builder.ret_void()

    return module


def _generate_reduction_kernel_tail_recursive(dtype) -> ir.Module:
    module = ir.Module()

    func_type = ir.FunctionType(
        return_type=dtype,
        args=(
            ir.PointerType(),
            i32,
            dtype,
        )
    )
    func_name = 'reduce_tail'
    func = ir.Function(
        module=module,
        ftype=func_type,
        name=func_name
    )

    xs, n, acc = func.args
    xs.name  = 'xs'
    n.name   = 'n'
    acc.name = 'acc'

    ZERO = ir.Constant(i32, 0)
    ONE = ir.Constant(i32, 1)

    entry_block = func.append_basic_block(name='entry')
    builder = ir.builder.IRBuilder(entry_block)

    cond = builder.icmp_signed(
        cmpop='==',
        lhs=n,
        rhs=ZERO,
        name='cond'
    )

    with builder.if_else(cond) as (then, otherwise):
        with then:
            builder.ret(acc)
        with otherwise:
            x = builder.load(
                ptr=xs,
                name='x',
                typ=dtype
            )
            new_xs = builder.gep(
                ptr=xs,
                indices=(ONE,),
                source_etype=dtype,
                name='new_xs'
            )
            new_n = builder.sub(n, ONE, name='new_n')
            new_acc = builder.xor(acc, x, name='new_acc')
            return_val = builder.call(
                fn=func,
                args=(
                    new_xs,
                    new_n,
                    new_acc
                ),
                tail=True
            )
            builder.ret(return_val)

    # this should never be executed
    builder.unreachable()

    return module


def generate_reduction_kernel(dtype) -> ir.Function:
    module = _generate_reduction_kernel_tail_recursive(dtype)
    tail_recursive_kernel = module.functions[0]

    func_type = ir.FunctionType(
        return_type=dtype,
        args=(
            ir.PointerType(),
            dtype,
        )
    )
    func_name = 'reduce'
    func = ir.Function(
        module=module,
        ftype=func_type,
        name=func_name
    )

    xs, n = func.args
    xs.name = 'xs'
    n.name = 'n'
    ZERO = ir.Constant(i32, 0)

    entry_block = func.append_basic_block(name='entry')
    builder = ir.builder.IRBuilder(entry_block)

    result = builder.call(
        fn=tail_recursive_kernel,
        args=(xs, n, ZERO)
    )
    builder.ret(result)

    return func


def wrap_kernel(kernel: ir.Function, prevent_dce: bool = False) -> ir.Function:
    """
    Adds a new function to the kernel module that repeatedly calls the kernel.
    Employs an inline assembly trick to disable DCE
    """
    module = kernel.module

    func_type = ir.FunctionType(
        return_type=kernel.ftype.return_type,
        args=kernel.ftype.args+(i32,)
    )
    func_name = f'{kernel.name}_wrapped'
    func = ir.Function(
        module=module,
        ftype=func_type,
        name=func_name
    )

    xs, n, nruns = func.args
    ZERO = ir.Constant(i32, 0)
    ONE = ir.Constant(i32, 1)

    builder = ir.builder.IRBuilder()

    entry_block = func.append_basic_block(name='entry')
    error_block = func.append_basic_block(name='error')
    loop_block = func.append_basic_block(name='loop')
    exit_block = func.append_basic_block(name='exit')

    builder.position_at_start(entry_block)
    cond = builder.icmp_signed('<', n, ONE)
    br = builder.cbranch(cond, error_block, loop_block)

    builder.position_at_start(error_block)
    builder.ret(ZERO)

    builder.position_at_start(loop_block)
    i = builder.phi(i32, name='i')
    new_i = builder.add(i, ONE)
    i.add_incoming(ZERO, entry_block)
    i.add_incoming(new_i, loop_block)

    res = builder.call(kernel, (xs, n))
    loop_cond = builder.icmp_signed('<', i, n)
    builder.cbranch(loop_cond, loop_block, exit_block)

    builder.position_at_start(exit_block)
    builder.ret(res)

    return func

