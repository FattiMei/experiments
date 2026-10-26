import llvmlite
import llvmlite.ir as ir
import llvmlite.binding as llvm


def f_function(dtype, module) -> ir.Function:
    """
    This is the function to be applied to every element
    of the input array

    The transformation I'm targeting does not require to know
    anything about this function, except maybe that it won't have
    side effects
    """

    ftype = ir.FunctionType(
        return_type=dtype,
        args=(dtype,)
    )
    func = ir.Function(module, ftype, name='f')

    x, = func.args
    entry_block = func.append_basic_block(name='entry')
    builder = ir.builder.IRBuilder()
    builder.position_at_start(entry_block)
    builder.ret(x)

    return func


def producer_function(dtype, module) -> ir.Function:
    ftype = ir.FunctionType(
        return_type=ir.VoidType(),
        args=(
            ir.PointerType(),
            ir.IntType(32)
        )
    )
    func = ir.Function(module, ftype, name='producer')
    f = f_function(dtype, module)

    # a tail recursive implementation would be easier to write
    # but it won't be directly compatible with the loop fusion pass
    #
    # I write a for loop instead
    ptr, n = func.args
    ptr.name = 'ptr'
    n.name = 'n'

    entry_block = func.append_basic_block('entry')
    cond_block = func.append_basic_block('cond')
    body_block = func.append_basic_block('body')
    end_block = func.append_basic_block('end')

    builder = ir.builder.IRBuilder()
    builder.position_at_start(entry_block)
    builder.branch(cond_block)
    builder.position_at_start(cond_block)
    i = builder.phi(typ=ir.IntType(32), name='i')
    i.add_incoming(ir.Constant(ir.IntType(32),0), entry_block)
    cond = builder.icmp_signed('<', i, n)
    builder.cbranch(cond, body_block, end_block)

    builder.position_at_start(body_block)
    p = builder.gep(ptr, (i,), inbounds=True, name='p', source_etype=dtype)
    val = builder.call(f, (i,))
    builder.store(val, p)
    new_i = builder.add(i, ir.Constant(ir.IntType(32), 1))
    i.add_incoming(new_i, body_block)
    builder.branch(cond_block)

    builder.position_at_start(end_block)
    builder.ret_void()

    return func


def consumer_function(dtype, module) -> ir.Function:
    # use the same control flow as the producer function
    ftype = ir.FunctionType(
        return_type=dtype,
        args=(
            ir.PointerType(),
            ir.IntType(32)
        )
    )
    func = ir.Function(module, ftype, name='consumer')

    ptr, n = func.args
    ptr.name = 'ptr'
    n.name = 'n'

    entry_block = func.append_basic_block('entry')
    cond_block = func.append_basic_block('cond')
    body_block = func.append_basic_block('body')
    end_block = func.append_basic_block('end')

    builder = ir.builder.IRBuilder()
    builder.position_at_start(entry_block)
    builder.branch(cond_block)
    builder.position_at_start(cond_block)
    acc = builder.phi(typ=dtype, name='acc')
    acc.add_incoming(ir.Constant(dtype,0), entry_block)
    i = builder.phi(typ=ir.IntType(32), name='i')
    i.add_incoming(ir.Constant(ir.IntType(32),0), entry_block)
    cond = builder.icmp_signed('<', i, n)
    builder.cbranch(cond, body_block, end_block)

    builder.position_at_start(body_block)
    p = builder.gep(ptr, (i,), inbounds=True, name='p', source_etype=dtype)
    val = builder.load(p, typ=dtype)
    new_i = builder.add(i, ir.Constant(ir.IntType(32), 1))
    i.add_incoming(new_i, body_block)
    new_acc = builder.xor(acc, val)
    acc.add_incoming(new_acc, body_block)
    builder.branch(cond_block)

    builder.position_at_start(end_block)
    builder.ret(acc)

    return func


def compose_function(producer, consumer, module) -> ir.Function:
    """
    This function composes the producer and the consumer functions.
    The composition stores the intermediate results into a buffer.

    If the buffer is a function argument we can't ever expect to
    remove the stores, so I stack allocate a buffer. Heap allocations
    are another can of worms since it would have side effects.


    """
    ftype = ir.FunctionType(
        consumer.ftype.return_type,
        args=(ir.IntType(32),)
    )

    func = ir.Function(module, ftype, name='compose')
    n, = func.args
    n.name = 'n'

    entry_block = func.append_basic_block(name='entry')
    builder = ir.builder.IRBuilder(entry_block)
    ptr = builder.alloca(ir.IntType(32), size=n, name='ptr')
    builder.call(producer, args=(ptr, n))
    res = builder.call(consumer, args=(ptr, n))

    builder.ret(res)
    return func


def compose_function_static(compose_function, n: int, module) -> ir.Function:
    ftype = ir.FunctionType(
        compose_function.ftype.return_type,
        args=()
    )
    func = ir.Function(module, ftype, name=f'compose{n}')

    n = ir.Constant(ir.IntType(32), n)

    entry_block = func.append_basic_block('entry')
    builder = ir.builder.IRBuilder(entry_block)
    res = builder.call(compose_function, args=(n,))
    builder.ret(res)

    return func


if __name__ == '__main__':
    # llvm initialization, I'm not putting it in a separate scope
    # as I'm afraid of unwanted garbage collection
    llvm.initialize_all_targets()
    llvm.initialize_all_asmprinters()
    triple = llvm.get_default_triple()
    target = llvm.Target.from_triple(triple)
    target_machine = target.create_target_machine(opt=3)

    # this would have to be done in an exploration loop
    module = ir.Module()
    dtype = ir.IntType(32)
    N = 250

    producer = producer_function(dtype, module)
    consumer = consumer_function(dtype, module)
    composition = compose_function(producer, consumer, module)
    composition_static = compose_function_static(composition, N, module)

    module.triple = triple
    module_ir = str(module)
    modref = llvm.parse_assembly(module_ir)

    with open('input.ll', 'w') as file:
        file.write(module_ir)

    # llvmlite bindings don't support the loop fusion
    # I would have to use the PEPPO library
    pto = llvm.create_pipeline_tuning_options(speed_level=3)
    pass_builder = llvm.create_pass_builder(target_machine, pto)
    mpm = pass_builder.getModulePassManager()
    mpm.run(modref, pass_builder)

    print(modref)

