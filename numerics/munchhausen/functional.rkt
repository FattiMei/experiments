(define (pow base exp)
  (if (zero? exp)
    base
    (* base (pow base (sub1 exp)))))

(define cache
  (list->vector
    (map (lambda (d) (if (zero? d) 0 (pow d d)))
          (range 10))))

(define (is-munchhausen-tail n number acc)
  (if (> acc n)
    #f
    (if (zero? number)
      (= n acc)
      (let-values (((q digit) (quotient/remainder number 10)))
        (is-munchhausen-tail n q (+ acc (vector-ref cache digit)))))))

(define (is-munchhausen n)
  (is-munchhausen-tail n n 0))

; In a eager language, this code does many allocations!
; (for-each
;   (lambda (n)
;     (when (is-munchhausen n)
;       (displayln n)))
;   (range 440000000))

(let loop ((i 0))
  (when (is-munchhausen i)
    (displayln i))

  (when (< i 440000000)
    (loop (add1 i))))
