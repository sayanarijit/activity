<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class Pages extends CI_Controller {

  function __construct()
  {
		// constructor
    parent::__construct();
  }

	public function view_page( $page = "home",$param1 = null,$param2 = null )
	{
		// Function to load a page

    $data['title'] = $page." ".$param1;

    $this->load->view('pages/header',$data);

    $data["users"] = $this->main_model->list_users();
    $data["reportids"] = array();

    foreach ($data["users"] as $user){
      $data["reportids"][$user] = $this->main_model->list_reports($user);
    }

    $this->load->view('pages/navbar',$data);

    if ($page == "home")
    {
      # Home page
      if (isset($_POST["title"])&&(!empty($_POST["title"]))){
        $title = preg_replace("/[^A-Za-z0-9-]/","_",$_POST["title"]);
        if(in_array($title, $data["reportids"]["web"])){
          show_error("Title '".$_POST["title"]."' already exists in database. Try another title");
          die();
        }
        $cmd = "/bin/sudo ".script_path()." -id ".$title;
        $cmd .= " -hosts ".str_replace("\n"," ",preg_replace("/[^A-Za-z0-9.-]/","\n",$_POST["hosts"]));
        $cmd .= " -ping_check";
        $cmd .= isset($_POST["os_check"]) ? " -os_check" : "";
        $cmd .= isset($_POST["console_check"]) ? " -console_check" : "";
        $cmd .= isset($_POST["dump_config"]) ? " -dump_config" : "";
        $cmd .= isset($_POST["id_and_homedir_check"]) ? " -id_and_homedir_check ".$_POST["id_and_homedir_check_params"] : "";
        $cmd .= isset($_POST["mount_check"]) ? " -mount_check ".$_POST["mount_check_params"] : "";
        $cmd .= isset($_POST["port_scan"]) ? " -port_scan ".$_POST["port_scan_params"] : "";
        $output = shell_exec($cmd);
        header("Location: ".base_url()."web/".$title);
        die();
      }
      $this->load->view('pages/home',$data);
    }

    else if(in_array($page,$data["users"]))
    {
      # Report
      $data["user"] = $user = $page;
      $data["reportid"] = $id = $param1;
      $data["display"] = "all";
      $data["reports"] = array();

      if (isset($_POST)&&(!empty($_POST))){
        if (isset($_POST["display"])&&(!empty($_POST["display"]))){
          $data["display"] = $_POST["display"];
        };
        if(isset($_POST["clean"])&&($_POST["clean"] == "clean")){
          $this->main_model->delete("reports",array("user"=>$user,"reportid"=>$id));
          header("Location: ".base_url());
          die();
        }
      };

      if (in_array($id, $data["reportids"][$user])){
        $data["report"] = $this->db->get_where("reports",array("user"=>$user,"reportid"=>$id));
        $actions =$this->main_model->list_actions($user,$id);
        foreach ($actions as $a){
          $data["actions"][$a] = $this->db->get_where("reports",array("user"=>$user,"reportid"=>$id, "action"=>$a));
        }
      }else{
        show_404();
      };
      $this->load->view('pages/report',$data);
    }else{
      show_404();
    }
	}
}
