from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from datetime import date


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://vxfxezrkeewvvl:c7c1e9d6ae9fbe9215aeec5d8b2786e06372198925a4a8c877e8157137d1beef@ec2-23-22-156-110.compute-1.amazonaws.com:5432/d9r73j1seev6bj'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://xqpcdpftbyiqtm:dedd556b61b932addb5a9dbcbc7dd9236cc0496884bae3eb3e152d86a8dfd988@ec2-34-200-116-132.compute-1.amazonaws.com:5432/d8cviba3a9padr'
db = SQLAlchemy(app)
maindb = db.Table('maindb', db.metadata, autoload=True, autoload_with=db.engine)

# Base = automap_base()
# Base.prepare(db.engine, reflect=True)
# maindb = Base.classes.maindb

# @app.route("/query_test/", methods=["GET"])
# def reply_test():
#     name = request.json["name"]
#     timestap  =
#     print(name)
#     if name:
#         test = db.session.query(maindb).filter(maindb.c.mac_address=="8b20d37d47b52b298444971325218e759b516057").first()
#         print(test[3])
#         return (jsonify({"result": test[3]}), 201)
#     else:
#         return (jsonify({"result": "it works"}), 200)

@app.route("/query_test/", methods=["GET"])
def reply_test():
    name = request.json["location"]
    timestap  =
    print(name)
    if name:
        test = db.session.query(maindb).filter(maindb.c.mac_address=="8b20d37d47b52b298444971325218e759b516057").first()
        print(test[3])
        return (jsonify({"result": test[3]}), 201)
    else:
        return (jsonify({"result": "it works"}), 200)

@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(debug=True)