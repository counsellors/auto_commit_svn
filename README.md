# auto_commit_svn
A web server to auto commit svn for each special request.

##Requirement
python2.7
svn1.6+
pip1.8+

##Run
1. start flask server
`python app.py`

## Test
myrepo is a svn repository.

request like:
`curl -X GET "http://127.0.0.1:5011/ci/4bd30f402321f3a8ab48ae0234f15494?filename=myrepo"`