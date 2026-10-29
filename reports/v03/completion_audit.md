# v0.3 交付核对

设计、预览、切片与实际打印均已核对。原生文件和 3MF 的 SHA-256 与对应验证报告一致。2026-10-16 已在 A1 设备页核实 v0.3 作业 100% 完成、122/122 层，并保存全盘成品画面；自动跟进已暂停。

| 用户要求 | 已检查的结果 | 证据 |
| --- | --- | --- |
| 减薄外壳，保留电池框长宽，适配约 5 mm 电池 | 主体 24.5→21.9 mm；后盖底厚 1.6 mm；PCB 背面高度 13 mm；框内 57×37 mm；选择 503550，厚 5 mm | 原生 Parameters；fit_check_v03.json；export_validation_v03.json 的成品包络检查 |
| 按键凸起、弧面、双定位耳及前盖导槽 | 九帽凸出面板 1.8 mm，球冠高 0.8 mm；双耳总长 9.2 mm、宽 1.6 mm，导槽单边间隙 0.25 mm | 原生 Parameters、Button_*、FrontShell_v03；连续 0～0.6 mm 运动检查 |
| 屏幕边缘深度 1～2 mm | 玻璃至窗口边缘 1.6 mm，中央面板下沉；最坏玻璃包络至面板内侧 0.4 mm | fit_check_v03.json；README_v03.md；装配预览 |
| 缩小 TF 口并外倒角 | 窄口 11.6×1.9 mm，外扩倒角深 0.8 mm | 原生 V03TFThroatAndChamfer；Parameters；实际 CAD 装配预览 |
| 独立滑动开关帽（图 5、6） | 外部防滑帽、捕获凸缘及内部叉槽；叉槽 1.8×1.5 mm；壳体导轨可动 2.3 mm | 原生 PowerSlider_v03 与导轨布尔树；连续扫掠检查；用户 MSK12C02 尺寸图 |
| Type-C 口只在后盖，金属外廓总体加约 1 mm，倒角 | 后壳开口 10.4×4.6 mm，对应保守接口包络 9.4×3.6 mm；外扩倒角 0.8 mm | 原生 V03USBThroatAndChamfer；前后盖独立布尔树；fit_check_v03.json |
| 薄后盖、深沉孔、使用已有短螺丝（图 8～10） | 选 M2×5，头径 4 mm；后盖沉孔直径 4.6 mm，承力台阶 1.4 mm；穿过约 1.6 mm PCB 后啮合约 2 mm | 原生 Parameters、V03DeepHeadBore*、Hardware_Screw*；fit_check_v03.json |
| 匹配图 11 热熔螺母 | M2、长 2 mm、外径 3 mm；前盖预孔直径 2.8 mm、深 2.15 mm，入口导入面 | 原生 Parameters、V03InsertPilot*、Hardware_Insert*；README_v03.md |
| 先展示带 PCB、可分解的 3D 预览 | 59 个实际 CAD 网格，含 PCB、外壳、电池、喇叭、按键及紧固件；支持旋转、分解和透视 | microbyte-v03-assembly.html；已浏览器检验；最终回复于 2026-10-16 02:18:49 展示 |
| 等用户确认；约一小时无确认可自动打印 | 等待超过 60 分钟，未收到修改或取消；发送前再次核对板面清空、设备空闲和 A4 黑色 PLA | print_followup_state.json；本聊天最终回复和实时设备检查 |
| 全套一盘、A1、上次黑色材料 | 12 件同一盘；本机 Bambu Studio 实际发送；设备作业名 myMicrobyte_v03_A1_black_PLA_sliced；A4 黑色 PLA | print_project_validation_v03.json；A1_v03_printing.png |
| 实际打印完成 | A1 显示正确 v0.3 作业 100% 完成、122/122 层；摄像头可见前后盖和周边小件，无明显拉丝团失败；精细配合仍需实物试装 | A1_v03_completed.png；print_project_validation_v03.json；打印跟进已暂停 |

## 验证覆盖与试装边界

已检查 12 个有效单实体、12 个闭合打印网格、原生文件重新打开重算、CAD 与网格体积一致性、前后壳和保留 PCB 模型的干涉、按键与拨帽运动包络、503550 标称和 56×36×5 mm 成品包络。前盖外侧向下打印，屏幕下沉区域有支撑；九帽弧面向上，耳部下方有支撑；拨帽外侧向下。切片中的支撑设置已在 GUI 核对保留。

本次交付为用户请求的试装版。MSK12C02 图纸未标明电气总行程，实际两个档位到位情况仍须试装确认；热熔预孔配合与按键手感需按打印实物确认。缺少精确模型的插头使用保守包络，电池包装尺寸和 Type-C 电缆塑壳仍以实物为准。上述限制已在试装说明中交付，不将 CAD 检查等同于实物装配验证。
