<!DOCTYPE html>
<html>
<head/>
<body>
<?php

function tainte($src)
{
    $dst = $src + 0;
    return "<div id='". $dst."'>content</div>";
}

$array = array();
$array[] = 'safe' ;
$array[] = $_GET['userData'] ;
$array[] = 'safe' ;
$tainted = $array[1] ;

$tainted = tainte($tainted);

echo $tainted;

?>
<h1>Hello World!</h1>
</body>
</html>