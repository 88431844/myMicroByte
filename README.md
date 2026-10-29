# myMicroByte 掌机外壳设计

全部成果统一保存在本项目目录。完整文件列表见 [项目文件索引](项目文件索引.md)。

## 常用入口

| 内容 | 文件 |
|---|---|
| 最新整机交互装配／爆炸图（v0.10，原电池框） | [打开交互页面](output/assembly-guide-v10/index.html) |
| v0.10 整机爆炸图 | [查看图片](reports/v10/whole_exploded.png) |
| v0.10 装配效果图 | [查看图片](reports/v10/whole_assembled.png) |
| v0.10 可编辑 FreeCAD 总装模型 | [打开模型](output/v10/myMicrobyte_enclosure_v10.FCStd) |
| 电池扩容版 FreeCAD 模型（57×32 mm 框） | [打开模型](reports/battery_expansion/enlarged_frame_study.FCStd) |
| 电池扩容前后尺寸对比 | [PNG](reports/battery_expansion/电池扩容前后对比.png) · [PDF](reports/battery_expansion/电池扩容前后对比.pdf) |
| 两个扩容后盖／蓝色 PLA 打印工程 | [工程](printing/A1_blue_PLA_expanded_rear_2/myMicrobyte_expanded_rear_2_blue.3mf) · [切片](printing/A1_blue_PLA_expanded_rear_2/myMicrobyte_expanded_rear_2_blue.gcode.3mf) |
| 四套 v0.10／黑色 PLA 打印工程 | [工程](printing/A1_black_PLA_v10_4sets/myMicrobyte_v10_4sets_black.3mf) |
| 电池与连接器选购报告 | [查看报告](reports/battery_expansion/电池扩容与插头选购.md) |
| 下载目录移入的历版装配截图与调整参数 | [装配导出文件目录](reports/assembly_exports/) |

交互页面通常可直接在浏览器打开。`output/assembly-guide-v03-legacy/` 为早期页面，需要网络加载 Three.js；v0.10 页面内嵌脚本与模型。整机 v0.10 预览仍显示原电池框，扩容尺寸请看独立模型和对比图。

## 目录说明

| 目录 | 用途 |
|---|---|
| `output/` | 历版外壳 FCStd、STEP、STL、试装包，以及交互装配／爆炸图网页 |
| `reports/` | 效果图、爆炸图、配色图、尺寸图、几何检查和打印证据 |
| `reports/assembly_exports/v03…v10/` | 从下载目录移入的 44 张装配视图和 1 份装配调整 JSON，按版本整理 |
| `reports/battery_expansion/` | 电池扩容模型、尺寸对比图、选购报告及检查脚本 |
| `printing/` | 拓竹工程、切片文件、打印参数、打印记录及生成脚本 |
| `reference/` | PCB 资料、元件尺寸与实物反馈参考 |
| `freecad/` | 外壳生成、导出和校核脚本 |
| `fusion/` | 早期 Fusion 相关脚本 |

## 本次归档记录

2026-10-22 共移入 46 个文件：44 张装配视图、1 份装配调整 JSON、1 份早期交互 HTML。移动前后逐一校验 SHA-256。既有模型和报告原本已经在项目内，保留版本结构。

- [移动来源、目标位置与校验值](reports/file_organization/move_manifest.json)
- 项目外旧预览位置仅保留指向项目内 HTML 的兼容符号链接，避免先前分享的路径失效。
- 最新扩容后盖的打印文件和已有预览服务路径保留，便于继续使用。
