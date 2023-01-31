import re


def handle_re(re_result):
    if re_result:
        return re_result.group(1).strip()
    else:
        return None

# Gate Sweep Ext [00_02(1) ; 12_4_2022 8_45_32 AM]
def extract_metadata(fname):
    """
    Extracts metadata based on file's name. The default filename is exported as (where curly braces do not appear in the final string):

    {Test Name} [{device name}({run number}) ; {date} {time}]
    """

    # name of test
    test_name = handle_re(re.match("(.+)\[", fname))

    # device name
    device_name = handle_re(re.match(".+\[(.+)\(", fname))

    # run number
    run_num = handle_re(re.match(".+\((\d+)\)", fname))

    # date
    date = handle_re(re.match(".+;\s(\S+)\s", fname))

    # time
    time = handle_re(re.match(".+(\d+_\d+_\d+\s\w\w)\]", fname))
    
    return {"TestName": test_name,
            "DeviceName": device_name,
            "RunNum": run_num,
            "Date": date,
            "Time": time}


