import os
import pathlib
import argparse
import subprocess

def run_thru_mo(ov_path, path, test_list,mode):

  
  files=[]
  os.system("mkdir -p tf_mo_logs")
  for r,d,f in os.walk(path):
    for file in f:
      if '.pb' in file:
        files.append(os.path.join(r,file))
  
  for fname in files:
    if mode == 'UTEST':
      mo_args = " --input_model " + fname
    else:
      test_info=open(test_list, 'r') 
      all_models=test_info.readlines() 
      match = 0
      for model in all_models:
        #print("Model file is " + model)
        model=model.strip('\r\n')
        model_name, input_shape = model.split()
        file_name = os.path.basename(fname)
        if model_name == file_name:
          match = 1
          break
      if match == 0:
        continue 

    mo_out = str(pathlib.Path(fname).parent.absolute())
    
    if mode == 'UTEST':
      cmd = [ov_path + "/deployment_tools/model_optimizer/mo_tf.py", "--input_model", fname, "-o",mo_out ]
    else:
      cmd = [ov_path + "/deployment_tools/model_optimizer/mo_tf.py", "--input_model", fname,"--input_shape", input_shape, "-o",mo_out, "--data_type", "FP16" ]
    mo_log = "./tf_mo_logs/" + fname[10:].replace("/","_")
    mo_log, ext = os.path.splitext(mo_log)
    mo_log += ".log"

    print("File log {} exists?: {}".format(mo_log,os.path.exists(mo_log)))

    if not os.path.exists(mo_log):
      result = subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

      mo_log_file = open(mo_log, "w")
      mo_log_file.write(result.stdout.decode("utf-8"))
      mo_log_file.close()

      print("Log file written to " + mo_log)
    
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-i',
                      '--model_path',
                      help='enter input model(.pb) path',
                      required=True)
  parser.add_argument('-t',
                    '--test_list',
                    help='Give file name having test list',
                    required=True)
  parser.add_argument('-m',
                    '--mode',
                    help='Unit test=UTEST or Model Test=MTEST',
                    required=True)
  args = parser.parse_args()
  ov_path = os.environ['INTEL_OPENVINO_DIR']
  run_thru_mo(ov_path, args.model_path, args.test_list, args.mode)
