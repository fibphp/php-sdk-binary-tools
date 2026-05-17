

function test(n, p) {
  if(!p) return;
  var ii, jj;
	for (var i = 0; i <= n; i++) {
  	ii = i * i;
		for (var j = 0; j <= n; j++) {
  		jj = j * j;
			for (var k = 0; k <= n; k++) {
				if (i + j + k == n && ii + jj == k * k) {
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