<div class="col-md-3 left_col">
  <div class="left_col scroll-view">
    <div class="navbar nav_title" style="border: 0;">
      <a href="<?php echo base_url(); ?>" class="site_title"><span><i class="fa fa-dashboard"></i> Activity</span></a>
    </div>

    <div class="clearfix"></div>

    <!-- sidebar menu -->
    <div id="sidebar-menu" class="main_menu_side hidden-print main_menu">
      <div class="menu_section">
        <ul class="nav side-menu">
          <?php
            foreach ($reportids as $user => $ids) { ?>
              <li><a><i class="fa fa-user"></i> <?php echo $user; ?> <span class="fa fa-chevron-down"></span></a>
                <ul class="nav child_menu">
                  <?php foreach ($ids as $id) { ?>
                    <li><a href="<?php echo base_url().$user."/".$id;?>"><?php echo $id; ?></a></li>
                  <?php ;}; ?>
                </ul>
              </li>
          <?php ;}; ?>
        </ul>
      </div>
    </div>
    <!-- /sidebar menu -->
  </div>
</div>

<!-- top navigation -->
<div class="top_nav">
  <div class="nav_menu">
    <nav class="" role="navigation">
      <div class="nav toggle">
        <a id="menu_toggle"><i class="fa fa-bars"></i></a>
      </div>
    </nav>
  </div>
</div>
<!-- /top navigation -->
