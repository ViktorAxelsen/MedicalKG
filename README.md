# Medical Knowledge Graph (Medical-KG)

## Code Structure

- data
    - **medicine.txt**：药品实体名

    - **medicine2.txt**：补充的药品实体名

    - **element.txt**：成分实体名

    - **illness.txt**：疾病实体名

    - **abnormal.txt**：不良反应实体名

- **build_medical_kg.py**：导入Neo4j数据库

- **question_classifier.py**：问题分类模块代码

- **question_parser.py**：问题解析和答案返回模块代码

- **answer_search.py**：具体查询执行模块

- **qa.py**：QA系统入口

- **stat_count.py**：查询特定节点或关系的统计数据

- **visualization.py**：根据特定节点以及关系实现实时可视化

- **main.py**：整体系统入口文件

    > **整体分为5个入口：QA System, Visualization, Node Stat, Rel Stat, Cypher Query**

    + **args**

        + **--task**：指定入口，1表示QA，2表示Visualization，3表示Node Stat，4表示Rel Stat，5表示Cypher Query

        + **--label_keyword**：待查询或询问的节点label参数

        + **--r_dir**：待查询或询问的关系方向，分为“in”，“out”，“bi”三种模式

        + **--r_type**：待查询或询问的关系类型

        + **--cypher**：cypher高级查询

        + **支持任意未知的“--key val”形式的参数解析，默认作为节点的固有属性进行查询或询问**


## Usage

### Install required pacjakes
```shell
pip install -r requirements.txt
```

### **QA System**

> **启动问答模块**

- **执行以下命令**

```python
python main.py --task 1
```


### **Visualization**

> **启动可视化模块**

- **执行以下命令**

```python
python main.py --task 2 \
    --label_keyword [YOUR_LABEL_KEYWORD] \
    --r_dir [YOUR_R_DIR] \
    --r_type [YOUR_R_TYPE] \
    --[YOUR_PROP_1] [YOUR_VAL_1] \
    --[YOUR_PROP_2] [YOUR_VAL_2]
    ......
```

### **Count**

> **启动节点信息统计模块**

- **执行以下命令**

```python
python main.py --task 3 \
    --label_keyword [YOUR_LABEL_KEYWORD] \
    --[YOUR_PROP_1] [YOUR_VAL_1] \
    --[YOUR_PROP_2] [YOUR_VAL_2]
    ......
```

### **Count Relation**

> **启动关系统计模块**

- **执行以下命令**

```python
python main.py --task 4 \
    --label_keyword [YOUR_LABEL_KEYWORD] \
    --r_dir [YOUR_R_DIR] \
    --r_type [YOUR_R_TYPE] \
    --[YOUR_PROP_1] [YOUR_VAL_1] \
    --[YOUR_PROP_2] [YOUR_VAL_2]
    ......
```

### **Cypher Query**

> **启动Cypher查询模块**

- **执行以下命令**

```python
python main.py --task 5 --cypher [YOUR_CYPHER]
```
