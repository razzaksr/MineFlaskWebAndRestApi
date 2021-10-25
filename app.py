from datetime import datetime
from flask import Flask,render_template,request,redirect,jsonify,make_response, sessions
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

app = Flask(__name__)

# db configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/test'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
base=SQLAlchemy(app)



#model
class notes(base.Model):
    id=base.Column(base.Integer,primary_key=True)
    title=base.Column(base.String(255),nullable=False)
    what=base.Column(base.String(255),nullable=False)
    doc=base.Column(base.DateTime,default=datetime.utcnow)

    def insert(self):
        base.session.add(self)
        base.session.commit()
        return self

    def __init__(self,title,what):
        self.title=title
        self.what=what

    def __repr__(self) -> str:
        return f"{self.title} - {self.what}"
    


@app.route('/change/<int:num>',methods=['GET','POST'])
def edit(num):
    data=notes.query.filter_by(id=num).first()
    if request.method=="POST":
        data.title=request.form["title"]
        data.what=request.form["what"]
        base.session.add(data)
        base.session.commit()
        return redirect("/")
    return render_template('alter.html',one=data)

@app.route('/erase/<int:num>')
def remove(num):
    data=notes.query.filter_by(id=num).first()
    base.session.delete(data)
    base.session.commit()
    return redirect('/')


@app.route('/',methods=['GET','POST'])
def first():
    if request.method=="POST":
        pro=notes(request.form["title"],request.form["what"])
        base.session.add(pro)
        base.session.commit()
    else:
        #base.create_all()
        '''pro=notes('simple','sample')
        base.session.add(pro)
        base.session.commit()'''
    every=notes.query.all()
    return render_template('home.html',all=every)

if __name__ == '__main__':
    app.run(debug=True,port=8000)



class NotesSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = notes
        sqla_session = base.session
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True)
    what = fields.String(required=True)
    doc = fields.DateTime(required=False)



@app.route('/flask', methods = ['GET'])
def listingall():
    get_products = notes.query.all()
    product_schema = NotesSchema(many=True)
    products = product_schema.dump(get_products)
    return make_response(jsonify({"product": products}))


@app.route('/flask', methods = ['POST'])
def create_product():
    data = request.get_json()
    product_schema = NotesSchema()
    product = product_schema.load(data)
    result = product_schema.dump(product.insert())
    '''base.session.add(product)
    base.session.commit()'''
    return make_response(jsonify({"product": result}),200)

@app.route('/flask/<int:id>',methods=['GET'])
def listOne(id):
    data=notes.query.filter_by(id=id).first()
    sch=NotesSchema(many=False)
    read=sch.dump(data)
    return make_response(jsonify({'data':read}))

@app.route('/flask/<int:who>',methods=['DELETE'])
def dele(who):
    data=notes.query.filter_by(id=who).first()
    base.session.delete(data)
    base.session.commit()
    return make_response(jsonify({"who":data.title}))

@app.route('/flask/<int:which>',methods=['PUT'])
def update(which):
    data = request.get_json()
    readen=notes.query.get(which)

    if data.get('title'):
        readen.title=data['title']
    if data.get('what'):
        readen.what=data['what']
    
    base.session.add(readen)
    base.session.commit()

    sch=NotesSchema()
    hai=sch.dump(readen)


    return make_response(jsonify({"data":hai}))