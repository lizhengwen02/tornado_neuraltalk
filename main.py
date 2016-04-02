#!/usr/bin/env python
#_*_ coding:utf-8 _*_
import os, random, string, json
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options

ImageBase = "/Users/zwli/tornado_proj/image_caption/static/tornado_images"
define("port", default=8000, help="run on the given port", type=int)
def Execute(cmd):
	try:
		print cmd
		print 'Executint cmd...........'
		p = os.popen(cmd)
		return p.read()
	except Exception, e:
		return "NULL"

def GenerateCnnFeature():
	cmd = """python /Users/zwli/image_description/neuraltalk/neuraltalk/python_features/extract_features.py --caffe /Users/zwli/image_description/caffe --model_def /Users/zwli/image_description/neuraltalk/neuraltalk/python_features/deploy_features.prototxt --model /Users/zwli/image_description/neuraltalk/neuraltalk/model/VGG_ILSVRC_16_layers.caffemodel --files /Users/zwli/tornado_proj/image_caption/static/tornado_images/tasks.txt --out /Users/zwli/tornado_proj/image_caption/static/tornado_images/img.mat
	"""
	return Execute(cmd)

def Predict():
	cmd = """
		python /Users/zwli/image_description/neuraltalk/neuraltalk/predict_on_images.py /Users/zwli/image_description/neuraltalk/neuraltalk/cv/flickr8k_cnn_lstm_v1.p -r /Users/zwli/tornado_proj/image_caption/static/tornado_images/
	"""
	return Execute(cmd)

class UploadHandler(tornado.web.RequestHandler):
	def post(self, *args, **kargs):
		print "POST"
		fileInfo = self.request.files['file1'][0]
		fname = fileInfo['filename']
		print fname
		extension = os.path.splitext(fname)[1]
		fname = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(6))
		finalName = fname + extension
		out_file = open(os.path.join(ImageBase, finalName), 'w')
		out_file.write(fileInfo['body'])
		out_file.close()
		task_file = open(os.path.join(ImageBase, "tasks.txt"), 'w')
		task_file.write(finalName)
		task_file.close()
		res = GenerateCnnFeature()
		if res is "NULL":
			print 'Sorry, error in generate cnn feature'
			self.write("Sorry, error in generate cnn feature")
			return
		caption = Predict()
		if caption is "NULL":
			print 'Sorry, error in predict'
			self.write("Sorry, error in predict")
			return
		result_json = open(os.path.join(ImageBase, "result_struct.json"), "r")
		result = result_json.read()
		data = json.loads(result)
		img = data["imgblobs"][0]["img_path"]
		cap = data["imgblobs"][0]["candidate"]["text"]
		self.write("<img src=./static/tornado_images/" + img + " height='400'><br>" + cap + "<br>")
	def write_error(self, status_code, **kwargs):
		self.write("Gosh darnit, user! You caused a %d error." % status_code)

class Index(tornado.web.RequestHandler):
	def get(self):
		print "Index Page"
		self.render("index.html")
if __name__ == "__main__":
	tornado.options.parse_command_line()
	setting = {
		"static_path": os.path.join(os.path.dirname(__file__), "static") 
	}
	app = tornado.web.Application(
		handlers=[
			(r"/", Index),
			(r"/upload", UploadHandler)
		],
		**setting
	)
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
