SEMANTIC_MAP = {
    "location": {
        "keywords": ["地点", "位置", "在哪里", "在哪", "地址"],
        "fields": ["location", "address"],
        "type" : "composite"
    },
    "navigation": {
        "keywords": ["怎么去", "导航", "路线", "怎么到", "怎么走"],
        "field": "address",
        "type": "navigation"
    },
    "time": {
        "keywords": ["时间", "几点", "日期", "时候"],
        "fields": ["date", "time"],
        "type" : "composite"
    },
    "ticket": {
        "keywords": ["票", "价格", "多少钱", "购票", "票价", "买票", "团购"],
        "field": "ticket_info",
        "type" : "object"
    },
    "contact": {
        "keywords": ["电话", "联系", "邮箱"],
        "field": [
            "contact.phone",
            "contact.email"
        ],
        "type": "object"
    },
    "facilities":{
        "keywords": ["提供什么", "设施", "提供", ],
        "field": "facilities",
        "type": "string"
    },
    "rules":{
        "keywords": ["违禁品", "禁止", "要求", "注意"],
        "field": "rules",
        "type": "string"
    },
    "description": {
        "keywords": ["是什么", "简介", "介绍", ],
        "field":  "description",
        "type": "string"
    },
    "lineup":{
        "keywords": ["歌手", "演出选手", "乐队", "演出阵容", "都有谁", "参加", "参演"],
        "field": "lineup",
        "type": "list"
    },
    "exhibitors": {
        "keywords" : ["展品", "公司", "展览", "商品", "产品", "项目", ],
        "field" : "exhibitors",
        "type": "list"
    },
    "sessions" : {
        "keywords" : ["会场", "演讲", "演讲者", "研讨会", "讨论", "开会",],
        "field" : "sessions",
        "type": "list"
    },

}