

function test(n, p) {
	for (var i = 0; i <= n; i++) {
		for (var j = 0; j <= n; j++) {
			for (var k = 0; k <= n; k++) {
				if (p && i + j + k == n && i * i + j * j == k * k) {
					p(i, j, k);
				}
			}
		}
	}
}

function main() {
	var test_print = function (a, b, c) {
		console.log(`The result ${a}^2 + ${b}^2 = ${c}^2 !`);
	};
	console.time('All Used');
	console.time('First Used');
	test(1000, test_print);
	console.timeEnd('First Used');

	for (var i = 0; i <= 10; i++) {
		test(1000, null);
	}
	console.timeEnd('All Used');
}

main();