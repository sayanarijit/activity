<?php
$tableids = array();
foreach ($actions as $action => $report) {
  if ($action == "ping_check")
  {
    $table[$action] = array(array("Hostname", "Ping status"));
    $allhosts =  $pingable_hosts = $down_hosts = [];
    foreach($report->result_array() as $r){
      $allhosts[] = $r["hostname"];
      if ($r["exit_code"] == 0){
        $pingable_hosts[] = $r["hostname"];
        $rep["Ping status"][$r["hostname"]] = "Up";
        $table[$action][] = array($r["hostname"],"Up");
      }else{
        $down_hosts[] =  $r["hostname"];
        $rep["Ping status"][$r["hostname"]] = "Down";
        $table[$action][] = array($r["hostname"],"Down");
      };
    };
  }
  elseif ($action == "os_check")
  {
    $table[$action] = array(array("Hostname", "SSH status", "OS/Kernel", "Version/Release", "Arch"));
    $os = $arch = $dist = $ssh_reachable_hosts =  $ssh_unreachable_hosts = [];
    foreach($report->result_array() as $r){
      $host = $r["hostname"];
      if($r["stdout"] == ""){
        $ssh_unreachable_hosts[] =  $host;
        $rep["SSH status"][$host] = "Inaccessible";
        $table[$action][] = array($host,"Inaccessible","N/A","N/A","N/A");
      }elseif(explode(" ", $r["stdout"])[0] == "Linux"){
        $rep["SSH status"][$host] = "Accessible";
        $ssh_reachable_hosts[] = $host;
        $rep["OS/Kernel"][$host] = "Linux";
        $line1 = explode("\n", $r["stdout"])[0];
        if (count(explode("\n", $r["stdout"])) == 1){
          $rep["Version/Release"][$host] = "N/A";
        }else{
          $rep["Version/Release"][$host] = explode("\n", $r["stdout"])[1];
        };
        if (endswith("64", $line1)){
          $rep["Arch"][$host] = "64 bit";
          $arc = "64 bit";
          $table[$action][] = array($host,"Accessible","Linux",$rep["Version/Release"][$host],$arc);
        }else{
          $rep["Arch"][$host] = "32 bit";
          $arc = "32 bit";
          $table[$action][] = array($host,"Accessible","Linux",$rep["Version/Release"][$host],$arc);
        };
      }else{
        $rep["SSH status"][$host] = "Accessible";
        $ssh_reachable_hosts[] = $host;
        $line1 = explode("\n", $r["stdout"])[0];
        $rep["OS/Kernel"][$host] = explode(" ", $r["stdout"])[0];
        $rep["Version/Release"][$host] = explode(" ", $line1)[1];
        if (endswith("64", $line1)){
          $rep["Arch"][$host] = "64 bit";
          $arc = "64 bit";
        }else{
          $rep["Arch"][$host] = "32 bit";
          $arc = "32 bit";
        };
        $table[$action][] = array($host,"Accessible",explode(" ", $line1)[0],explode(" ", $line1)[1],$arc);
      }
    };
  }
  elseif($action == "console_check")
  {
    $table[$action] = array(array("Hostname", "Console available", "Consoles"));
    $console_available = $console_unavailable = [];
    foreach($report->result_array() as $r){
      $host = $r["hostname"];
      if($r["exit_code"] == 0){
        $console_available[] = $host;
        $rep["Console available"][$host] = "Yes";
        $rep["Consoles"][$host] = $host."-".implode("<br>".$host."-",json_decode($r["stdout"]));
        $table[$action][] = array($host,"Yes",$rep["Consoles"][$host]);
      }else{
        $console_unavailable[]  = $host;
        $rep["Console available"][$host] = "No";
        $rep["Consoles"][$host] = "N/A";
        $table[$action][] = array($host,"No","N/A");
      }
    }
  }
  elseif($action == "dump_config")
  {
    $headings = array("Hostname",
      "uname -a", "cat /etc/*release", "uptime", "ifconfig -a", "netstat -nr",
      "cat /etc/fstab", "cat /etc/vfstab", "cat /etc/mtab", "cat /etc/network/interfaces",
      "cat /etc/sysconfig/network", "cat /etc/nsswitch.conf", "cat /etc/yp.conf",
      "cat /etc/ssh/sshd_config", "cat /etc/puppet.conf", "cat /etc/sudoers",
      "cat /etc/sudoers.d/*", "cat /usr/local/etc/sudoers", "cat /usr/local/etc/sudoers.d/*"
    );
    $table[$action] = array($headings);
    foreach($report->result_array() as $r){
      $host = $r["hostname"];
      $arr = array($host);
      $outputs = explode("[---x---]", $r["stdout"]);
      $i = 1;
      foreach($outputs as $o){
        $arr[] = $o;
        $rep[$headings[$i]][$host] = $o;
        $i += 1;
      };
      $table[$action][] = $arr;
    };
  }
  elseif(explode(" ",$action)[0] == "execute:")
  {
    $table[$action] = array(array("Hostname", "Command", "Stdout", "Stderr", "Exit code"));
    foreach($report->result_array() as $r){
      $host = $r["hostname"];
      $title = explode(" ",$action)[1];
      $rep[$title.": command"][$host] = $r["command"];
      $rep[$title.": stdout"][$host] = $r["stdout"];
      $rep[$title.": stderr"][$host] = $r["stderr"];
      $rep[$title.": exit_code"][$host] = $r["exit_code"];
      $table[$action][] = array($host, $r["command"], $r["stdout"], $r["stderr"], $r["exit_code"]);
    };
  }
  elseif(explode(" ",$action)[0] == "port_scan:")
  {
    $table[$action] = array(array("Hostname", "Port status"));
    foreach($report->result_array() as $r){
      $host = $r["hostname"];
      $port = explode(" ",$action)[1];
      $rep["Port ".$port." status"][$host] = (($r["exit_code"]==0) ? "Open" : "Closed");
      $table[$action][] = array($host, (($r["exit_code"]==0) ? "Open" : "Closed"));
    };
  }
  elseif(explode(" ",$action)[0] == "scp:")
  {
    $table[$action] = array(array("Hostname", "SCP status"));
    foreach($report->result_array() as $r){
      $host = $r["hostname"];
      $path = explode(" ",$action)[1];
      $rep["SCP status: ".$path][$host] = (($r["exit_code"]==0) ? "Success" : "Failed");
      $table[$action][] = array($host, (($r["exit_code"]==0) ? "Success" : "Failed"));
    };
  }
  elseif(explode(" ",$action)[0] == "mount_check:")
  {
    $table[$action] = array(array("Hostname", "Mounted", "Writable", "Disk usage"));
    foreach($report->result_array() as $r){
      $host = $r["hostname"];
      $vol = explode(" ",$action)[1];
      $mounted = $rep["Mounted: ".$vol][$host] = (count(explode("\n",$r["stdout"])) > 4) ? "Yes" : "No";
      if ($mounted == "Yes"){
        $writable = $rep["Writable: ".$vol][$host] = (count(explode("\n",$r["stdout"])) > 5) ? "Yes" : "No";
        $arr = explode(" ",explode("%",$r["stdout"])[0]);
        $d_usage = $rep["Disk usage: ".$vol][$host] = end($arr)."%";
      }else{
        $writable = $rep["Writable: ".$vol][$host] = "N/A";
        $d_usage = $rep["Disk usage: ".$vol][$host] = "N/A";
      };
      $table[$action][] = array($host, $mounted, $writable, $d_usage);
    };
  }
  elseif(explode(" ",$action)[0] == "id_and_homedir_check:")
  {
    $table[$action] = array(array("Hostname", "ID present", "Homedir present", "Has write permission"));
    foreach($report->result_array() as $r){
      $host = $r["hostname"];
      $u = explode(" ",$action)[1];
      $id = $rep["ID present: ".$u][$host] = (count(explode("\n",$r["stdout"])) > 2) ? "Yes" : "No";
      if ($id == "Yes"){
        $home = $rep["Homedir present: ".$u][$host] = (count(explode("\n",$r["stdout"])) > 3) ? "Yes" : "No";
        if($home == "Yes"){
          $perm = $rep["Has write permission: ".$u][$host] = (count(explode("\n",$r["stdout"])) > 4) ? "Yes" : "No";
        }else{
          $perm = $rep["Has write permission: ".$u][$host] = "N/A";
        }
      }else{
        $home = $rep["Homedir present: ".$u][$host] = "N/A";
        $perm = $rep["Has write permission: ".$u][$host] = "N/A";
      };
      $table[$action][] = array($host, $id, $home, $perm);
    };
  };
};
?>


<div class="right_col" role="main">

  <!--- Quick counts --->
  <div id="counts" class="row tile_count">
    <div class="col-md-2 col-sm-4 col-xs-6 tile_stats_count">
      <span class="count_top">Total hosts</span>
      <div id="total_hosts" class="count"><?php echo count($allhosts); ?></div>
    </div>
    <div class="col-md-2 col-sm-4 col-xs-6 tile_stats_count">
      <span class="count_top">Hosts up</span>
      <div id="up_hosts" class="count green"><?php echo count($pingable_hosts); ?></div>
    </div>
    <div class="col-md-2 col-sm-4 col-xs-6 tile_stats_count">
      <span class="count_top">Hosts down</span>
      <div id="down_hosts" class="count red"><?php echo count($down_hosts); ?></div>
    </div>
    <?php if(isset($ssh_reachable_hosts)&&(isset($ssh_unreachable_hosts))){ ?>
      <div class="col-md-2 col-sm-4 col-xs-6 tile_stats_count">
        <span class="count_top">SSH reachable</span>
        <div id="reachable_hosts" class="count green"><?php echo count($ssh_reachable_hosts); ?></div>
        <span class="count_bottom">(out of all pingable hosts)</span>
      </div>
      <div class="col-md-2 col-sm-4 col-xs-6 tile_stats_count">
        <span class="count_top">SSH unreachable</span>
        <div id="unreachable_hosts" class="count red"><?php echo count($ssh_unreachable_hosts); ?></div>
        <span class="count_bottom">(out of all pingable hosts)</span>
      </div>
    <?php ;}; ?>
  </div>
  <!--- Controls --->
  <div class="row">
    <div class="col-md-12 col-sm-12 col-xs-12">
      <div class="x_panel">
        <div class="x_content">
          <form id="formA" action="" method="post" data-parsley-validate="" class="form-horizontal form-label-left" novalidate="">
            <div class="btn-group" data-toggle="buttons">
              <label class="btn btn-default <?php echo (($display == 'all') ? 'active' : '');?>">
                <input type="radio" name="display" value="all"> Display all in one
              </label>
              <label class="btn btn-default  <?php echo (($display == 'individual') ? 'active' : '');?>">
                <input type="radio" name="display" value="individual"> Display individually
              </label>
            </div>
          </form>
          <?php if ($user == "web") { ?>
            <div class="ln_solid"></div>
            <form action="" method="post" data-parsley-validate="" class="form-horizontal form-label-left" novalidate="">
              <button type="submit" name="clean" value="clean" class="btn btn-round btn-danger">Clean this report</button>
            </form>
          <?php ;}; ?>
        </div>
      </div>
    </div>
  </div>
  <!--- Tables --->
  <div class="row">
    <div class="col-md-12 col-sm-12 col-xs-12">
      <div class="x_panel">
        <div class="x_title">
          <h2>Reports</h2>
          <ul class="nav navbar-right panel_toolbox">
            <li><a class="collapse-link"><i class="fa fa-chevron-up"></i></a>
            </li>
            <li><a class="close-link"><i class="fa fa-close"></i></a>
            </li>
          </ul>
          <div class="clearfix"></div>
        </div>
        <div class="x_content">
          <?php if ($display == "all") {
            $headings = array_merge(["Hostname"], array_keys($rep));
            $data["tabledata"] = array($headings);
            // print_r($headings);
            foreach($allhosts as $host){
              $row = array($host);
              foreach ($rep as $action => $report) {
                if(isset($report[$host])){
                  $row[] = $report[$host];
                }else{
                  $row[] = "N/A";
                }
              }
              $data["tabledata"][] = $row;
            }
            // print_r($data["tabledata"]);
            $tableids[] = $data["tableid"] = rand(11111111,99999999);
            $this->load->view('pages/table',$data);
          }else{ ?>
            <div class="accordion" id="accordion" role="tablist" aria-multiselectable="true">
              <?php foreach ($actions as $action => $report) { $elem = rand(11111111,99999999); $elems[] = $elem; ?>
                <div class="panel">
                  <a class="panel-heading collapsed" role="tab" data-toggle="collapse" data-parent="#accordion" href="#<?php echo $elem; ?>" aria-expanded="false" aria-controls="<?php echo $elem; ?>">
                    <h4 class="panel-title text-center"><?php echo str_replace("_", " ", $action); ?></h4>
                  </a>
                  <div id="<?php echo $elem; ?>" class="panel-collapse collapse" role="tabpanel" aria-expanded="false" style="height: 0px;">
                    <div class="panel-body">
                      <div class="" role="tabpanel" data-example-id="togglable-tabs">
                        <ul class="nav nav-tabs bar_tabs" role="tablist">
                          <li role="presentation" class="active"><a href="#<?php echo $elem; ?>-validation" role="tab" data-toggle="tab" aria-expanded="true">Validation</a>
                          </li>
                          <li role="presentation" class=""><a href="#<?php echo $elem; ?>-raw_output" role="tab" data-toggle="tab" aria-expanded="false">Raw output</a>
                          </li>
                        </ul>
                        <div  class="tab-content">
                          <div role="tabpanel" class="tab-pane active fade in" id="<?php echo $elem; ?>-validation">
                            <?php
                              $data["tabledata"] = $table[$action];
                              // Display table
                              $tableids[] = $data["tableid"] = rand(11111111,99999999);
                              $this->load->view('pages/table',$data);
                            ?>
                          </div>
                          <?php
                            // Raw output
                            if (in_array(explode(" ",$action)[0], array("ping_check","os_check","id_and_homedir_check:","mount_check:",)))
                            {
                                echo '<div role="tabpanel" class="tab-pane fade in" id="'.$elem.'-raw_output">';
                                $data["tabledata"] = $report;
                                $tableids[] = $data["tableid"] = rand(11111111,99999999);
                                $this->load->view('pages/table',$data);
                                echo "</div>";
                            };
                            ?>
                          <div role="tabpanel" class="tab-pane fade in" id="<?php echo $elem; ?>-stats">
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <p>&nbsp;</p>
              <?php ;}; ?>
            </div>
          <?php ;}; ?>
        </div>
      </div>
    </div>
  </div>
</div>
<!-- /page content -->
<?php $this->load->view('pages/scripts'); ?>
<script>
  $(document).ready(function() {
    $("input[name='display']").change(function(){
      $("#formA").submit();
    });
    <?php foreach($tableids as $id) { ?>
      $('#<?php echo $id; ?>').DataTable({
        // sDom: 'Rlfrtip',
        colReorder: true,
        dom: 'Bfrtp',
        pagination: false,
        buttons: [
            'colvis', 'copyHtml5', 'excelHtml5', 'csvHtml5', 'pdfHtml5'
        ]
      });
    <?php ;}; ?>
  } );
</script>
<?php $this->load->view('pages/footer'); ?>
