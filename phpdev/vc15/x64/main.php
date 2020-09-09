<?php

function test($n, $p)
{
    for ($i = 0; $i <= $n; $i++) {
        for ($j = 0; $j <= $n; $j++) {
            for ($k = 0; $k <= $n; $k++) {
                if (!empty($p) && $i + $j + $k == $n && $i * $i + $j * $j == $k * $k) {
                    $p($i, $j, $k);
                }
            }
        }
    }
}

function main()
{
    $start = microtime(true);

    $test_print = function ($a, $b, $c) {
        echo "The result {$a}^2 + {$b}^2 = {$c}^2 !\n";
    };

    test(1000, $test_print);
    $cost1 = microtime(true) - $start;
    echo"First Used {$cost1} seconds\n";

    for ($i = 0; $i <= 10; $i++) {
        # test(1000, null);
    }
    $cost = microtime(true) - $start;
    echo"All Used {$cost} seconds\n";
}


main();