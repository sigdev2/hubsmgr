mkdir gittest
cd gittest

rem test: pysync
mkdir pysync
cd pysync
git init .
echo test text > test.txt
git add test.txt
git commit -m "init"
cd ../

rem test: clone local
mkdir clone_local
cd clone_local
git init .
echo test text > test.txt
git add test.txt
git commit -m "init"
cd ../

rem test: clone cloned
mkdir cloned
cd cloned
git clone ../clone_local .
cd ../

rem test: autocommit
mkdir autocommit
cd autocommit
git init .
echo test text > test.txt
git add test.txt
git commit -m "init"
cd ../

rem test: freeze
mkdir freeze
cd freeze
git init .
echo test text > test.txt
git add test.txt
git commit -m "init"
cd ../

rem test: nosub
mkdir nosub
cd nosub
git init .
echo test text > test.txt
git add test.txt
git commit -m "init"
cd ../

rem test: notags
mkdir notags
cd notags
git init .
echo test text > test.txt
git add test.txt
git commit -m "init"
cd ../

rem test: branch
mkdir branch
cd branch
git init .
echo test text > test.txt
git add test.txt
git commit -m "init"
git branch test
git checkout test
echo test text > branch.txt
git add branch.txt
git commit -m "branch"
git checkout master
cd ../

rem test: tag
mkdir tag
cd tag
git init .
echo test text > test.txt
git add test.txt
git commit -m "init"
git tag test
echo test text > overtag.txt
git add overtag.txt
git commit -m "overtag"
cd ../

rem test: push test
mkdir push
cd push
git init .
echo test text > test.txt
git add test.txt
git commit -m "init"
git config receive.denyCurrentBranch updateInstead
cd ../

rem test: free tags
mkdir freetags
cd freetags
git init .
echo test text > test.txt
git add test.txt
git commit -m "init"
echo freetag.txt > .gitignore
git add .gitignore
git commit -m "gitignore"
echo test text > freetag.txt
git update-index --add freetag.txt
git write-tree > tree_hash.txt
For /f "delims=" %%a in ('Type "tree_hash.txt"') do (git tag fasttag %%a)
For /f "delims=" %%a in ('Type "tree_hash.txt"') do (git tag -a freetag %%a -m "with comment")
del tree_hash.txt
cd ../

rem test: managed
mkdir managed_source
cd managed_source
git init .
echo test text > test.txt
git add test.txt
git commit -m "init"
cd ../../
mkdir managed_target

rem test: many hubs
mkdir manyhubs1
cd manyhubs1
mkdir manyhub
cd manyhub
git init .
echo test text > test1.txt
git add test1.txt
git commit -m "init"
git config receive.denyCurrentBranch updateInstead
cd ../../

mkdir manyhubs2
cd manyhubs2
mkdir manyhub
cd manyhub
git init .
echo test text > test2.txt
git add test2.txt
git commit -m "init"
git config receive.denyCurrentBranch updateInstead
cd ../../

mkdir manyhubs3
cd manyhubs3
mkdir manyhub
cd manyhub
git init .
echo test text > test3.txt
git add test3.txt
git commit -m "init"
git config receive.denyCurrentBranch updateInstead
cd ../../

rem handle tests:
rem  - fixed revision
rem  - push