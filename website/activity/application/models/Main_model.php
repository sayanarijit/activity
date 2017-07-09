<?php
class Main_model extends CI_Model {

    function __construct()
    {
        // Call the Model constructor
        parent::__construct();
    }

    function list_users(){
      $data = $this->db->distinct()->select("user")->get("reports")->result_array();
      $users = array();
      foreach ($data as $k => $v) {
        foreach ($v as $k => $u){
          $users[] = $u;
        }
      }
      return $users;
    }

    function list_reports($user){
      $where = array("user"=>$user);
      $data = $this->db->distinct()->select("reportid")->where($where)->get("reports")->result_array();
      $reports = array();
      foreach ($data as $k => $v) {
        foreach ($v as $k => $r){
          $reports[] = $r;
        }
      }
      return $reports;
    }

    function list_actions($user,$id){
      $where = array("user"=>$user,"reportid"=>$id);
      $data = $this->db->distinct()->select("action")->where($where)->get("reports")->result_array();
      $actions = array();
      foreach ($data as $k => $v) {
        foreach ($v as $k => $a){
          $actions[] = $a;
        }
      }
      return $actions;
    }

    function get($table,$limit=null,$offset=null)
    {
        $query = $this->db->get($table,$limit,$offset);
        return $query->result_array();
    }

    function count_all($table)
    {
        return $this->db->count_all($table);
    }

    function count_where($table,$where)
    {
        return $this->db->where($where)->count_all_results($table);
    }

    function get_where($table,$where,$limit=null,$offset=null)
    {
        $query = $this->db->get_where($table,$where,$limit,$offset);
        return $query->result_array();
    }

    function match_where($table,$where,$string)
    {
        $s_array = explode(' ',$string);
        foreach($s_array as $s){
          $query = $this->db->like($table,$s);
        }
        $query = $this->db->get_where($table,$where);
        return $query->result_array();
    }

    function update($table, $data, $where)
    {
        $this->db->update($table, $data, $where);
    }

    function insert($table, $data)
    {
        $this->db->insert($table, $data);
        return $this->db->insert_id();
    }

    function delete($table, $where)
    {
        $this->db->delete($table, $where);
    }
}
?>
