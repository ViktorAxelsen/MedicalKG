# Medical Knowledge Graph (Medical-KG)

## Code Structure

- **build_medical_kg.py**：导入Neo4j数据库

- **medicine.txt**：药品实体名

- **medicine2.txt**：补充的药品实体名

- **element.txt**：成分实体名

- **illness.txt**：疾病实体名

- **abnormal.txt**：不良反应实体名

- **question_classifier.py**：问题分类模块代码

- **stat_count.py**：查询特定节点或关系的统计数据

- **visualization.py**：根据特定节点以及关系实现实时可视化

- **main.py**：整体系统入口文件

    > **整体分为5个入口：QA System, Visualization, Node Stat, Rel Stat, Cypher Query**

    + **args**

        + **--task**：指定入口，1表示QA，2表示Visualization，3表示Node Stat，4表示Rel Stat，5表示Cypher Query

        + **--label_keyword**：待查询或询问的节点label参数

        + **--r_dir**：待查询或询问的关系方向，分为“in”，“out”，“bi”三种模式

        + **--r_type**：待查询或询问的关系类型

        + **支持任意未知的“--key val”形式的参数解析，默认作为节点的固有属性进行查询或询问**


