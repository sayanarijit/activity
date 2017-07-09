<?php

function script_path()
{
  // Mention the path to activity script here
  return "/script/activity/activity.py";
}

function colorit($data)
{
  // Function to color and format report fields

  $color["yes"] = "green";
  $color["up"] = "green";
  $color["accessible"] = "green";
  $color["good"] = "green";
  $color["open"] = "green";
  $color["success"] = "green";

  $color["no"] = "red";
  $color["down"] = "red";
  $color["inaccessible"] = "red";
  $color["bad"] = "red";
  $color["closed"] = "red";
  $color["failed"] = "red";

  $color["n/a"] = "orange";
  $color["Unknown"] = "orange";

  $data = in_array(strtolower($data), array_keys($color)) ? "<span style='color: ".$color[strtolower($data)]."'>".$data."</span>" : $data;
  return nl2br($data);
}

function startswith($needle, $haystack) {
  // search backwards starting from haystack length characters from the end
  return $needle === "" || strrpos($haystack, $needle, -strlen($haystack)) !== false;
}

function endswith($needle, $haystack) {
  // search forward starting from end minus needle length characters
  return $needle === "" || (($temp = strlen($haystack) - strlen($needle)) >= 0 && strpos($haystack, $needle, $temp) !== false);
}
?>
