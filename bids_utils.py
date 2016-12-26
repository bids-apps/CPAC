import os
import yaml

def gen_bids_outputs_sublist(base_path,paths_list,key_list,creds_path):

    import copy 

    func_keys = [ "functional_to_anat_linear_xfm", "motion_params", "movement_parameters", "motion_correct" ]
    top_keys = list(set(key_list) - set(func_keys))
    bot_keys = list(set(key_list).intersection(func_keys))

    print top_keys
    print bot_keys

    subjdict = {}

    if not base_path.endswith('/'):
        base_path=base_path+'/'

    # output directories are a bit different than standard BIDS, so 
    # we handle things differently

    for p in paths_list:
        p = p.rstrip()

        # find the participant and session info which should be at
        # some level in the path
        path_base=p.replace(base_path,'')

        subj_info=path_base.split('/')[0]
        resource=path_base.split('/')[1]

        if resource not in key_list:
            continue

        if subj_info not in subjdict:
            subjdict[subj_info]={"subj_info":subj_info}

        if creds_path:
            subjdict[subj_info]["creds_path"]=creds_path

        if resource in func_keys:
            run_info=path_base.split('/')[2]
            if "funcs" not in subjdict[subj_info]:
                subjdict[subj_info]["funcs"]={}
            if run_info not in subjdict[subj_info]["funcs"]:
                subjdict[subj_info]["funcs"][run_info]={'run_info':run_info} 
            if resource in subjdict[subj_info]["funcs"][run_info]:
                print "warning resource %s already exists in subjdict ??"%(resource)
            subjdict[subj_info]["funcs"][run_info][resource]=p
        else:
            subjdict[subj_info][resource]=p
            
    sublist = []
    for subj_info,subj_res in subjdict.iteritems():
        missing=0
        for tkey in top_keys:
            if tkey not in subj_res:
                 print "%s not found for %s"%(tkey,subj_info)
                 missing+=1
                 break

        if missing == 0:
            for func_key,func_res in subj_res["funcs"].iteritems():
                for bkey in bot_keys:
                    if bkey not in func_res:
                        print "%s not found for %s"%(bkey,func_key)
                        missing+=1
                        break
                if missing == 0:
                    print "adding: %s, %s, %d"%(subj_info,func_key,len(sublist))
                    tdict=copy.deepcopy(subj_res)
                    del tdict["funcs"]
                    tdict.update(func_res)
                    sublist.append(tdict)
    return sublist

def gen_bids_sublist(paths_list,creds_path):

    subdict = {}

    for p in paths_list:
        p = p.rstrip()
        f = os.path.basename(p)
        if f.endswith(".nii") or f.endswith(".nii.gz"):
            f_dict={}
            for key_val_pair in f.split("_"):
                key_val_pair=key_val_pair.lower()
                if not "nii" in key_val_pair:
                    chunks = key_val_pair.split("-")
                    f_dict[chunks[0]] = "-".join(chunks[1:])
                else:
                    f_dict["scantype"] = key_val_pair.split(".")[0]

            if "ses" not in f_dict:
                f_dict["ses"] = "1"

            if "sub" not in f_dict:
                raise IOError("sub not found in %s, perhaps it isn't in BIDS format?"%(p))

            if f_dict["sub"] not in subdict:
                subdict[f_dict["sub"]] = {}

            if f_dict["ses"] not in subdict[f_dict["sub"]]:
                subdict[f_dict["sub"]][f_dict["ses"]]=\
                {"creds_path":creds_path,\
                 "subject_id":"-".join(["sub",f_dict["sub"]]),\
                 "unique_id":"-".join(["ses",f_dict["ses"]])}

            if "t1w" in f_dict["scantype"]:
                if not "anat" in subdict[f_dict["sub"]][f_dict["ses"]]:
                    subdict[f_dict["sub"]][f_dict["ses"]]["anat"]=p
                else:
                    print "Anatomical file (%s) already found for (%s:%s) discarding %s"%(\
                        subdict[f_dict["sub"]][f_dict["ses"]]["anat"],
                        f_dict["sub"],
                        f_dict["ses"],
                        p)

            if "bold" in f_dict["scantype"]:
                task_key = "-".join(["task",f_dict["task"]])
                if "run" in f_dict:
                    task_key = "_".join([task_key,\
                        "-".join(["run",f_dict["run"]])])
                if "acq" in f_dict:
                    task_key = "_".join([task_key,\
                        "-".join(["acq",f_dict["acq"]])])
                if not "rest" in subdict[f_dict["sub"]][f_dict["ses"]]:
                    subdict[f_dict["sub"]][f_dict["ses"]]["rest"]=\
                        {task_key:p}
                elif not task_key in \
                    subdict[f_dict["sub"]][f_dict["ses"]]["rest"]:
                    subdict[f_dict["sub"]][f_dict["ses"]]["rest"][task_key]=p
                else:
                    print "Func file (%s) already found for (%s:%s:%s) discarding %s"%(\
                        subdict[f_dict["sub"]][f_dict["ses"]]["rest"][task_key],
                        f_dict["sub"],
                        f_dict["ses"],
                        task_key,
                        p)

    sublist = []
    for sub in subdict.itervalues():
        for ses in sub.itervalues():
            if "anat" in ses and "rest" in ses:
                sublist.append(ses)
            else:
                print "No anat or rest found for %s %s"%(ses["subject_id"],
                    ses["unique_id"])
    
    return sublist

def test_gen_bids_sublist(paths_file,test_yml):

    paths_list=[]
    with open(paths_file, "r") as fd:
        paths_list=fd.readlines()

    print len(paths_list)
    sublist=gen_bids_sublist(paths_list)

    with open(test_yml,"w") as ofd:
        yaml.dump(sublist, ofd)

    assert(sublist)

if __name__ == '__main__':
    test_gen_bids_sublist("test/rs_bucket_list.txt", "test/rs_subject_list.yml")

