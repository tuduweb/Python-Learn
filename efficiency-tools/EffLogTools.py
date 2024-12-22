import re
import xlwt
import xlrd
import os
import argparse
import subprocess
import json

def extract_values_from_string(input_string, template):
    input_string = input_string.replace('autogen_', '')

    # 定义正则表达式，匹配模板中的每个占位符，并提取相应的值
    pattern = re.sub(r'\{\$(\w+)\}', r'(?P<\1>\\w+)', template)
    
    # 匹配输入字符串
    match = re.match(pattern, input_string)
    
    if match:
        # 提取所有匹配的占位符值，返回字典
        return match.groupdict()
    else:
        return None  # 如果没有匹配上，返回 None

class efficiency_log_item_info(object):
    file_key: str
    file_path: str
    max_efficiency: float
    pass

class efficiency_log_tool(object):
    class efficiency_log_tool_debug_cfg(object):
        print_internal_log = 1

    debug_cfg   = efficiency_log_tool_debug_cfg()

    eff_keyword = "eff"

    _ptc_file_key_list = {
        "v20241220": "a2_{$freq}_x8_{$addrmap_id}_size{$burst_size}_len{$burst_len}_{$trans_mode}_ots{$outstanding}_{$addr_mode}_{$ecc}",
        "v20241221": "a4_{$freq}_x8_{$addrmap_id}_size{$burst_size}_len{$burst_len}_{$trans_mode}_ots{$outstanding}_id{$id_mode}_{$addr_mode}_{$ecc}"
    }

    #######
    ## return: Eff Files
    def FindEffLogFilesInDirectory(self, directoryPath) -> list:
        ### init vals
        eff = 0.0
        eff_infos = []

        ### program start
        for root, dirs, files in os.walk(directoryPath):
            # walk all tghe file in direct
            for file_item in files:
                print("="*150)
                file_path = os.path.join(root, file_item)
                if self.eff_keyword in file_item:
                    print("file:", file_path)
                    ret = self.ParsePTCLogName(file_item)
                    print("filename", ret["tc_key"])
                    ret = self.FindEffInfoInLog(file_path)
                    print("max_eff = %0f" % ret["eff"])
                    eff_infos.append(ret)
                print("*"*150)

        return eff_infos
    
    def ParsePTCLogName(self, ptcLogNameString: str) -> str:
        pattern = r'^(.+)_tc_([\w\d_]+)_(\d+).run_log'
        result  = re.match(pattern, ptcLogNameString)

        ## init params
        tc_key = ""
        tc_seed = ""

        if result:
            # print("tc_name=", result.group(1))
            # print("params =", result.group(2))
            # print("seed   =", result.group(3))
            tc_name= result.group(1)
            tc_key = result.group(2)
            tc_seed= result.group(3)
        else:
            print("ptc parse unknown")
        
        dictGroup = self.StartToMatchPTCNamePattern(tc_key)

        return {
            "tc_name"   : "%0s_tc_%0s" % (os.path.basename(tc_name), tc_key),
            "tc_key"    : tc_key,
            "tc_seed"   : tc_seed,
            "key_param" : dictGroup
        }

    def ParseUVMLogItem(self, uvmLogItemString: str) -> list:
        pattern = r'^(UVM_[A-Z]+) @ (\d+\.\d+[nf]s): reporter \[([\w\d]+)\] (.*)'
        result  = re.match(pattern, uvmLogItemString)

        info_lvl   = ""
        info_ts    = ""
        info_cls   = ""
        info_detail= ""

        if result:
            info_lvl   = result.group(1)
            info_ts    = result.group(2)
            info_cls   = result.group(3)
            info_detail= result.group(4)

        # print(result.group(2))
        # print(result.group(3))
        # print(result.group(4))

        return {
            "info_lvl"      : info_lvl,
            "info_ts"       : info_ts,
            "info_cls"      : info_cls,
            "info_detail"   : info_detail
        }

        pass
    
    def ParseEffItremLog(self, effLogString: str) -> list:
        ret = self.ParseUVMLogItem(effLogString)
        print(ret)
        pass

    def ParseEffMaxString(self, effMaxString: str) -> float:
        pattern = r'^current max_eff=(\d+\.\d+)'
        result  = re.match(pattern, effMaxString)
        eff = 0.0
        if result:
            eff = float(result.group(1))
        
        print("final eff=%0f" % eff)

        return eff

    def _parse_simu_end_of_log_consume(self, consumeLog: str) -> dict:
        consumeRetDict = {
            "cpu_time": -1,
            "cpu_time_unit": "us",
            "data_size": "unknown"
        }
        consumeLog = consumeLog.strip()
        pattern = r"CPU Time:\s*(\d+\.\d+)\s*seconds;\s*Data structure size:\s*(\d+\.\d+\s*Mb|Gb|GB)"
        result = re.match(pattern, consumeLog)
        if result:
            print(result)
            consumeRetDict["cpu_time"] = result.group(1)
            consumeRetDict["data_size"] = result.group(2)
        else:
            print("_parse_simu_end_of_log_consume not matched")
        
        print(consumeRetDict)

        return consumeRetDict
    
    def _parse_simu_end_of_log_datetime(self, dateLog: str) -> dict:

        from datetime import datetime
        # 输入的日期字符串
        date_string = dateLog # "Fri Dec 20 16:39:41 2024"
        # 解析日期字符串，格式字符串需要与输入的时间格式完全匹配
        date_object = datetime.strptime(date_string, "%a %b %d %H:%M:%S %Y")
        # 输出解析后的 datetime 对象
        print(date_object)

        return {
            "datetime": str(date_object)
        }

    def _parse_simu_end_of_log_simuTime(self, simuTimeLog: str) -> dict:
        simuTimeLog = simuTimeLog.strip()
        pattern = r"Time:\s*(\d+)\s*(fs|ps|us|ns)"
        time_in_us = 0.0
        result = re.match(pattern, simuTimeLog)
        if result:
            time_value = int(result.group(1))  # 时间值
            unit = result.group(2)  # 单位
            # 将飞秒 (fs) 转换为纳秒 (ns)
            time_in_ns = time_value * 1e-6  # 1 fs = 10^-6 ns
            time_in_us = time_value * 1e-9  # 1 fs = 10^-6 ns
            print("time_in_ns", time_in_ns)
        pass
        
        return {
            "simu_time": time_in_us
        }

    def ParseSimuEndOfLog(self, endOfLogStringList: list):
        # Parse Running Time
        # endOfLogStringList[]
        # simu_log ['Time: 282752000000 fs\n', 'CPU Time:    987.640 seconds;       Data structure size: 231.9Mb\n', 'Fri Dec 20 16:39:41 2024']
        dict_title = ["simu_time", "consume", "endtime"]
        simuLogDict = {
            "simu_time": 0.0,
            "simu_consume": {},
            "endtime": "unknown"
        }
        

        for idx, itemString in enumerate(endOfLogStringList):
            if "CPU Time" in itemString:
                ret = self._parse_simu_end_of_log_consume(itemString)
                simuLogDict["simu_consume"] = ret
            elif "Time" in itemString:
                ret = self._parse_simu_end_of_log_simuTime(itemString)
                simuLogDict["simu_time"] = ret["simu_time"]
            else:
                ret = self._parse_simu_end_of_log_datetime(itemString)
                simuLogDict["endtime"] = ret["datetime"]

        return simuLogDict

    
    def ParseBandwidthLog(self, bandWidthLog: []) -> [dict]:
        
        # ====================FLOW INFO====================
        # ===================================================
        # write flow[Max    ]:[0.000000][GBps]
        # write flow[Min    ]:[0.000000][GBps]
        # write flow[Average]:[0.000000][GBps]
        # read  flow[Max    ]:[10200.382897][GBps]
        # read  flow[Min    ]:[8200.716846][GBps]
        # read  flow[Average]:[9112.395706][GBps]
        # wcmd  num          :[0][____]
        # wdata num          :[0][____]
        # rcmd  num          :[10000][____]
        # ===================================================

        ret = []
        for idx, logItem in enumerate(bandWidthLog):
            retDict = {}
            if ":" in logItem:
                # print(idx, logItem.strip())
                pattern = r"([\s\w]+)\[(\w+)\s*\]:\[(\d+\.\d+)\]\[GBps\]"
                matches = re.search(pattern, logItem)
                if matches:
                    retDict["perf_name"]  = matches.group(1)
                    retDict["perf_type"]  = matches.group(2)
                    retDict["perf_value"] = matches.group(3)
                    # print(matches.group(1))
                    # print(matches.group(2))
                    # print(matches.group(3))
                    ret.append(retDict)
                else:
                    # print("not matched")
                    pass

        return ret

    def FindEffInfoInLog(self, effInfoLogFilePath) -> dict:
        retDict = {
            "ptc_name"      : "",
            "key_param"     : {},
            "ptc_path"      : effInfoLogFilePath,
            "ptc_seed"      : "",
            "ptc_abspath"   : os.path.abspath(os.path.join(os.getcwd(), effInfoLogFilePath)),
            "eff"           : 0.0,
            "bandwidth"     : {}
        }
        print("file", effInfoLogFilePath)

        ret = self.ParsePTCLogName(effInfoLogFilePath)
        retDict["ptc_name"]     = ret["tc_name"]
        retDict["ptc_seed"]     = ret["tc_seed"]
        retDict["key_param"]    = ret["key_param"]

        eff = 0.0

        with open(effInfoLogFilePath, 'r') as f:
            lineItems = f.readlines()[-500:]
            # print(lineItems)

            for idx, lineLog in enumerate(lineItems):
                if "report_ddr_result" in lineLog and "current max_eff" in lineLog:
                    print("eff_max_log:", lineLog)
                    # print("parse", self.ParseUVMLogItem(lineLog))
                    ret = self.ParseUVMLogItem(lineLog)
                    eff = self.ParseEffMaxString(ret["info_detail"])
                    continue
                elif "report_ddr_result" in lineLog:
                    # print("eff_log:", lineLog.strip())
                    ##  TODO: parse one line log
                    ##  UVM_INFO @ 282752.0000ns: reporter [report_ddr_result] [38] diff_time=6232 wr_cnt=0 rd_cnt=602 wr_eff=0.000000 rd_eff=0.386393 eff=0.386393
                    ret = self.ParseEffItremLog(lineLog)
                    pass
                elif "FLOW INFO" in lineLog:
                    # ====================FLOW INFO====================
                    # ===================================================
                    # write flow[Max    ]:[0.000000][GBps]
                    # write flow[Min    ]:[0.000000][GBps]
                    # write flow[Average]:[0.000000][GBps]
                    # read  flow[Max    ]:[10200.382897][GBps]
                    # read  flow[Min    ]:[8200.716846][GBps]
                    # read  flow[Average]:[9112.395706][GBps]
                    # wcmd  num          :[0][____]
                    # wdata num          :[0][____]
                    # rcmd  num          :[10000][____]
                    # ===================================================
                    print("flow_info", idx, idx+11)
                    ret = self.ParseBandwidthLog(lineItems[idx: idx+11])
                    retDict["bandwidth"] = ret
                    # find ===================================================
                    pass
                elif "Interval Start Time" in lineLog:
                    # =======================================================================================
                    # (nop)
                    # Interval Start Time                          : 270000.000000 ns                 ;  Interval End Time                            : 280000.000000 ns                 
                    # (nop)
                    # Configured max read xact latency             : 1000000.000000 ns                ;  Observed max read xact latency               : 643.497870 ns                    
                    # Configured min read xact latency             : 1.000000 ns                      ;  Observed min read xact latency               : 142.493160 ns                    
                    # Configured avg_max read xact latency         : 1000000.000000 ns                ;  Observed avg_max read xact latency           : 170.624975 ns                    
                    # Configured avg_min read xact latency         : 1.000000 ns                      ;  Observed avg_min read xact latency           : 170.624975 ns                    
                    # (nop)
                    # =======================================================================================

                    print("latency_info", idx, idx + 6)
                    pass
                elif "V C S   S i m u l a t i o n   R e p o r t " in lineLog:
                    print("simu_log", lineItems[idx+1: idx+4])
                    # start to parse simu end log
                    ret = self.ParseSimuEndOfLog(lineItems[idx+1: idx+4])
                    retDict["uvm_log"] = ret
                    pass
        
        retDict["eff"] = eff

        return retDict


    def ConvertLogToExcel(self, inputList: list) -> int:
        xlwt_workbook = xlwt.Workbook()
        xlwt_sheet    = xlwt_workbook.add_sheet("eff")
        xlwt_cur_row  = 0

        xlwt_header = ["ptc_name", "freq", "burst_size", "burst_len", "outstanding", "id_mode", "addr_mode", "ptc_path", "max_eff", "perf_read_avg", "perf_write_avg", "perf_rw_avg", "simu_time", "cpu_time", "data"]

        for idx, item in enumerate(xlwt_header):
            xlwt_sheet.write(0, idx, item)

        xlwt_cur_row  = 1

        for idx, effItem in enumerate(inputList):
            xlwt_sheet.write(xlwt_cur_row, 0, effItem["ptc_name"])
            xlwt_sheet.write(xlwt_cur_row, 1, effItem["key_param"]["freq"])
            xlwt_sheet.write(xlwt_cur_row, 2, effItem["key_param"]["burst_size"])
            xlwt_sheet.write(xlwt_cur_row, 3, effItem["key_param"]["burst_len"])
            xlwt_sheet.write(xlwt_cur_row, 4, effItem["key_param"]["outstanding"])
            xlwt_sheet.write(xlwt_cur_row, 5, effItem["key_param"].get("id_mode", "rand"))
            xlwt_sheet.write(xlwt_cur_row, 6, effItem["key_param"]["addr_mode"])
            xlwt_sheet.write(xlwt_cur_row, 7, effItem["ptc_abspath"])
            xlwt_sheet.write(xlwt_cur_row, 8, effItem["eff"])
            xlwt_sheet.write(xlwt_cur_row, 9, float(effItem["bandwidth"][2+3]["perf_value"]) / 1000)
            xlwt_sheet.write(xlwt_cur_row, 10, float(effItem["bandwidth"][2]["perf_value"]) / 1000)
            xlwt_sheet.write(xlwt_cur_row, 11, (float(effItem["bandwidth"][2]["perf_value"]) + float(effItem["bandwidth"][2+3]["perf_value"])) / 1000)
            xlwt_sheet.write(xlwt_cur_row, 12, effItem["uvm_log"]["simu_time"])
            xlwt_sheet.write(xlwt_cur_row, 13, effItem["uvm_log"]["simu_consume"]["cpu_time"])
            xlwt_sheet.write(xlwt_cur_row, 14, json.dumps(effItem))
            xlwt_cur_row = xlwt_cur_row + 1

        xlwt_workbook.save("eff.xlsx")

        return 0

    def StartToMatchPTCNamePattern(self, ptcNameMatchedString: str) -> dict:
        for keyName, keyPattern in self._ptc_file_key_list.items():
            print(keyPattern)
            placeholders = re.findall(r'\{\$(\S+?)\}', keyPattern)
            print(placeholders)

            groupDict = extract_values_from_string(ptcNameMatchedString, keyPattern)
            if groupDict != None:
                print(groupDict)
                return groupDict

        return None

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='DDR EFF TOOLs')
    parser.add_argument('--filepath', type=str, help='filePath to eff regress file path', default="", required=True)
    args = parser.parse_args()

    eff_log_tool = efficiency_log_tool()

    print("start running FindEffLogFilesInDirectory")
    detInfo = eff_log_tool.FindEffLogFilesInDirectory(args.filepath)
    
    eff_log_tool.ConvertLogToExcel(detInfo)

    print("detInfo", len(detInfo))
    if len(detInfo) > 0:
        print(detInfo[0])
    # eff_log_tool.FindEffInfoInLog("./eff_log.log")

    # eff_log_tool.ParsePTCLogName("tc908_efficiency_tc_cust_2400_timing1_axi_rand_16B_4len_rd_9121004789.run_log")

    eff_log_tool.StartToMatchPTCNamePattern("autogen_a2_2666_x8_map0_size5_len4_rd_ots16_rand_noecc")

    pass
