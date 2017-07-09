<div style="height: 250px; width: 400px" id="<?php echo $chartid; ?>">
</div>
<script>
document.addEventListener("DOMContentLoaded", function(event) {
  Morris.Bar({
    element: '<?php echo $chartid; ?>',
    data: [
      { y: '2006', a: 100, b: 90 },
      { y: '2007', a: 75,  b: 65 },
      { y: '2008', a: 50,  b: 40 },
      { y: '2009', a: 75,  b: 65 },
      { y: '2010', a: 50,  b: 40 },
      { y: '2011', a: 75,  b: 65 },
      { y: '2012', a: 100, b: 90 }
    ],
    xkey: 'y',
    ykeys: ['a', 'b'],
    labels: ['Series A', 'Series B'],
    xLabelAngle: 60
  });
})
</script>
