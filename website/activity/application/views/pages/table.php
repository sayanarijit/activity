<div style="overflow: auto;">
<?php
  $template = array(
          'table_open'            => '<table id="'.$tableid.'" class="table table-striped table-bordered no-footer dtr-inline">',

          'thead_open'            => '<thead>',
          'thead_close'           => '</thead>',

          'heading_row_start'     => '<tr>',
          'heading_row_end'       => '</tr>',
          'heading_cell_start'    => '<th>',
          'heading_cell_end'      => '</th>',

          'tbody_open'            => '<tbody style="white-space: nowrap; color: #079">',
          'tbody_close'           => '</tbody>',

          'row_start'             => '<tr>',
          'row_end'               => '</tr>',
          'cell_start'            => '<td>',
          'cell_end'              => '</td>',

          'row_alt_start'         => '<tr>',
          'row_alt_end'           => '</tr>',
          'cell_alt_start'        => '<td>',
          'cell_alt_end'          => '</td>',

          'table_close'           => '</table>'
  );
  $this->table->set_template($template);

  if(is_array($tabledata)){
    $this->table->function = 'colorit';
    echo $this->table->generate($tabledata);
  }else{
    $this->table->function = 'nl2br';
    echo $this->table->generate($tabledata);
  }
?>
</div>
