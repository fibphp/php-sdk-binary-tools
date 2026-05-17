package main

import (
	"fmt"
	"time"
)

func test(n int, p func(int, int, int)) {
	for i := 0; i <= n; i++ {
		for j := 0; j <= n; j++ {
			for k := 0; k <= n; k++ {
				if p != nil && i+j+k == n && i*i+j*j == k*k {
					p(i, j, k)
				}
			}
		}
	}
}

func test_print(a, b, c int) {
	fmt.Printf("The result %d^2 + %d^2 = %d^2 !\n", a, b, c)
}

func main() {
	start := time.Now()

	test(1000, test_print)
	cost1 := time.Since(start)
	fmt.Printf("First Used %s\n", cost1)

	for i := 0; i <= 10; i++ {
		test(1000, nil)
	}

	cost := time.Since(start)
	fmt.Printf("All Used %s\n",cost)
}
