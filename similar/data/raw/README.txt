此目录用于存放原始蛋白质数据CSV文件。

实际生产环境中，应将以下文件放置在此目录：
1. protein_data.csv - 包含蛋白质ID、功能、EC编号、GO术语等信息的CSV文件

CSV文件应包含以下列：
- Protein_ID: 蛋白质的UniProt ID
- Representation: 蛋白质的480维表征向量（文本格式的列表）
- Function: 蛋白质的功能描述
- EC: 酶委员会编号列表
- GO: 基因本体论术语列表
- Domain: 蛋白质结构域列表
- SubcellularLocation: 亚细胞定位信息
- SequenceFeature: 序列特征信息
- InterProFamily: InterPro蛋白质家族信息 