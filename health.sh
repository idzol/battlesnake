# Update URL to match ..
url='https://battlesnake-dev.idzol.repl.co'
health=`curl -Is $url | head -n 1`
pattern='200'
if [[ $health == *"$pattern"* ]]; then
  echo "True"
  # mail -s "Battlesnake - UP" p.kubik@gmail.com
else 
  echo "False"
  
  # mail -s "Battlesnake - DOWN" p.kubik@gmail.com
fi
