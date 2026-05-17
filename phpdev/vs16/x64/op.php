<?php

$start = microtime(true);

$m = 'main.php';
if (!in_array('--no-pause', $argv)) {
    exec('pause');
}

$ret = opcache_compile_file($m);
print_r($ret);

echo "file {$m} ret:", opcache_is_script_cached($m) ? 1 : 0, "\n";
$cost = microtime(true) - $start;
echo "All Used {$cost} seconds\n";

$ret = opcache_get_status(true);
// var_dump($ret);
