# CoderProfiler
make coder profile based on data from github

MySQL：10.1.1.61 端口号36810，用户名密码都是visitor

for proj in Projlist:
  find last Commit C0, run git reset C0, pmd C0, => C0 obj, update com_list, init vio_pre_list(list of vio_pre_obj)
  C1 = C0
  for Cj = Ci.parent != null and  looptime < LOOPTIME:
    run git reset Cj, pmd Cj, =>Cj obj, update com_list, update vio_pre_list
    
  for vv_pre in vio_pre_list:
    back loop vv_pre.pre_list, => this vio kind pre_time.dis_time
  
  sort dis_time/pre_time, => imp_vio_list
  
  for com in com_list(imp_vio_list):
    for file in com_file_list:
      get file's score
      => update com.dev's score
      
