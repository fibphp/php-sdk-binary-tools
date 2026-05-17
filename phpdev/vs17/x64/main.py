import datetime

def test(n, p):
    if not p:
        return
    nn = range(0, n+1)
    for i in nn:
        ii = i * i
        for j in nn:
            jj = j * j
            for k in range(n-i-j, n-i-j+1):
                if i+j+k==n and ii+jj==k*k:
                    p(i, j, k)

def test_print(a, b, c):
    print "The result %d^2 + %d^2 = %d^2 !" % (a, b, c)

def main():
    starttime = datetime.datetime.now()

    test(1000, test_print)
    print "First Used %f seconds" % ((datetime.datetime.now() - starttime).seconds, )

    for i in range(0, 10):
        test(1000, None)

    print "All Used %f seconds" % ((datetime.datetime.now() - starttime).seconds, )

if __name__ == '__main__':
    main()
