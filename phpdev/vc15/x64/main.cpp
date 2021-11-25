#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#if defined(__clang__)
    #define NO_INLINE __attribute__((noinline))
#else
    #define NO_INLINE
#endif

static void  test(int n, void (*p)(int, int, int)) 
NO_INLINE
{
    for (int i = 0; i <= n; i++)
    {
        for (int j = 0; j <= n; j++)
        {
            for (int k = 0; k <= n; k++)
            {
                if (p && i + j + k == n && i * i + j * j == k * k)
                {
                    p(i, j, k);
                }
            }
        }
    }
}

static void test_print(int a, int b, int c)
NO_INLINE
{
    printf("The result %d^2 + %d^2 = %d^2 !\n", a, b, c);
}

int main()
{
    clock_t start, finish;
    start = clock();
    double duration;

    test(1000, test_print);
    finish = clock();
    duration = (double)(finish - start) / CLOCKS_PER_SEC;
    printf("First Used %f seconds\n", duration);

    for (int i = 0; i <= 10; i++)
    {
        test(1000, NULL);
    }

    finish = clock();
    duration = (double)(finish - start) / CLOCKS_PER_SEC;
    printf("All Used %f seconds\n", duration);
    return 0;
}
