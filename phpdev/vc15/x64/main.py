import datetime

def test(n, p):
    for i in range(0, n):
        for j in range(0, n):
            for k in range(0, n):
                if p and i+j+k==n and i*i+j*j==k*k:
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
