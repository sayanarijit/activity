<!-- page content -->
<div class="right_col" role="main">
  <div class="row">
    <div class="col-md-12 col-sm-12 col-xs-12">
      <div class="x_panel">
        <div class="x_title">
          <h2>Start a new activity</h2>
          <ul class="nav navbar-right panel_toolbox">
            <li><a class="collapse-link"><i class="fa fa-chevron-up"></i></a>
            </li>
            <li><a class="close-link"><i class="fa fa-close"></i></a>
            </li>
          </ul>
          <div class="clearfix"></div>
        </div>
        <div class="x_content">
          <br>
          <form action="" method="post" data-parsley-validate="" class="form-horizontal form-label-left" novalidate="">
            <div class="col-md-4 col-sm-12 col-xs-12 form-group">
              <input type="text" required class="form-control" name="title" placeholder="Title">
              <p>&nbsp;</p>
              <textarea required class="form-control" rows="10" name="hosts" placeholder="Server list"></textarea>
            </div>

            <div class="col-md-4 col-sm-6 col-xs-6 form-group">
              <div class="checkbox">
                <label>
                  <div class="icheckbox_flat-green checked disabled" style="position: relative;">
                    <input type="checkbox" name="ping_check" class="flat" disabled="disabled" checked="checked" style="position: absolute; opacity: 0;">
                    <ins class="iCheck-helper" style="position: absolute; top: 0%; left: 0%; display: block; width: 100%; height: 100%; margin: 0px; padding: 0px; background: rgb(255, 255, 255); border: 0px; opacity: 0;"></ins>
                  </div> Ping check
                </label>
              </div>
            </div>
            <div class="col-md-4 col-sm-6 col-xs-6 form-group">
              <p>&nbsp;</p>
            </div>

            <div class="col-md-4 col-sm-6 col-xs-6 form-group">
              <div class="checkbox">
                <label>
                  <div class="icheckbox_flat-green checked disabled" style="position: relative;">
                    <input type="checkbox" name="os_check" class="flat" style="position: absolute; opacity: 0;">
                    <ins class="iCheck-helper" style="position: absolute; top: 0%; left: 0%; display: block; width: 100%; height: 100%; margin: 0px; padding: 0px; background: rgb(255, 255, 255); border: 0px; opacity: 0;"></ins>
                  </div> OS check (or SSH check)
                </label>
              </div>
            </div>
            <div class="col-md-4 col-sm-6 col-xs-6 form-group">
              <p>&nbsp;</p>
            </div>

            <div class="col-md-4 col-sm-6 col-xs-6 form-group">
              <div class="checkbox">
                <label>
                  <div class="icheckbox_flat-green checked disabled" style="position: relative;">
                    <input type="checkbox" name="console_check" class="flat" style="position: absolute; opacity: 0;">
                    <ins class="iCheck-helper" style="position: absolute; top: 0%; left: 0%; display: block; width: 100%; height: 100%; margin: 0px; padding: 0px; background: rgb(255, 255, 255); border: 0px; opacity: 0;"></ins>
                  </div> Console check
                </label>
              </div>
            </div>
            <div class="col-md-4 col-sm-6 col-xs-6 form-group">
              <p>&nbsp;</p>
            </div>

            <div class="col-md-4 col-sm-4 col-xs-6 form-group">
              <div class="checkbox">
                <label>
                  <div class="icheckbox_flat-green checked disabled" style="position: relative;">
                    <input type="checkbox" name="dump_config" class="flat" style="position: absolute; opacity: 0;">
                    <ins class="iCheck-helper" style="position: absolute; top: 0%; left: 0%; display: block; width: 100%; height: 100%; margin: 0px; padding: 0px; background: rgb(255, 255, 255); border: 0px; opacity: 0;"></ins>
                  </div> Dump config
                </label>
              </div>
            </div>
            <div class="col-md-4 col-sm-6 col-xs-6 form-group">
              <p>&nbsp;</p>
            </div>

            <div class="col-md-4 col-sm-6 col-xs-6 form-group">
              <div class="checkbox">
                <label>
                  <div class="icheckbox_flat-green checked disabled" style="position: relative;">
                    <input type="checkbox" name="id_and_homedir_check" class="flat" style="position: absolute; opacity: 0;">
                    <ins class="iCheck-helper" style="position: absolute; top: 0%; left: 0%; display: block; width: 100%; height: 100%; margin: 0px; padding: 0px; background: rgb(255, 255, 255); border: 0px; opacity: 0;"></ins>
                  </div> ID and homedir check
                </label>
              </div>
            </div>
            <div class="col-md-4 col-sm-6 col-xs-6 form-group">
              <input name="id_and_homedir_check_params" disabled type="text" class="form-control" placeholder="e.g. root user1 user2">
            </div>

            <div class="col-md-4 col-sm-6 col-xs-6 form-group">
              <div class="checkbox">
                <label>
                  <div class="icheckbox_flat-green checked disabled" style="position: relative;">
                    <input type="checkbox" name="mount_check" class="flat" style="position: absolute; opacity: 0;">
                    <ins class="iCheck-helper" style="position: absolute; top: 0%; left: 0%; display: block; width: 100%; height: 100%; margin: 0px; padding: 0px; background: rgb(255, 255, 255); border: 0px; opacity: 0;"></ins>
                  </div> Mount check
                </label>
              </div>
            </div>
            <div class="col-md-4 col-sm-6 col-xs-6 form-group">
              <input name="mount_check_params" disabled type="text" class="form-control" placeholder="e.g. /tmp /var/log /mnt">
            </div>

            <div class="col-md-4 col-sm-6 col-xs-6 form-group">
              <div class="checkbox">
                <label>
                  <div class="icheckbox_flat-green checked disabled" style="position: relative;">
                    <input name="port_scan" type="checkbox" class="flat" style="position: absolute; opacity: 0;">
                    <ins class="iCheck-helper" style="position: absolute; top: 0%; left: 0%; display: block; width: 100%; height: 100%; margin: 0px; padding: 0px; background: rgb(255, 255, 255); border: 0px; opacity: 0;"></ins>
                  </div> Port scan
                </label>
              </div>
            </div>
            <div class="col-md-4 col-sm-6 col-xs-6 form-group">
              <input name="port_scan_params" disabled type="text" class="form-control" placeholder="e.g. 22 80 443">
            </div>
            <p>&nbsp;</p>
            <button type="submit" class="btn btn-primary btn-block">Start</button>
          </form>
        </div>
      </div>
      <p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p>
    </div>
  </div>
</div>
<!-- /page content -->
<?php $this->load->view('pages/scripts'); ?>
<script>
  $(document).ready(function() {
    $(".checkbox label").click(function(){
       var name = $(this).find('> div > div > input').attr("name");
       $("input[name='"+name+"_params']").val("");
       $("input[name='"+name+"_params']").prop("disabled", function(i, v) { return !v; });
       $("input[name='"+name+"_params']").prop("required", function(i, v) { return !v; });
    })
  })
</script>
<?php $this->load->view('pages/footer'); ?>
