## Quick start

- Install Vagrant and VirtualBox
- Clone the fullstack-nanodegree-vm
- Launch the Vagrant VM (vagrant up)
- Clone the repo: `git clone https://github.com/meowtsai/catalog-app.git` under `/vagrant/catalog/` folder
- run `python models.py` to create database
- run `python lotsofitems.py` to insert dummy data
- run `pip install --upgrade google-auth` so the google login works properly
- run `python project.py`
- make sure port 5000 is listed in Vagrantfile. `config.vm.network "forwarded_port", guest: 5000, host: 5000, host_ip: "127.0.0.1"`
- Access this app by visiting http://localhost:5000 locally

## Features

### API Endpoints
- [JSON endpoint displays all the categories along with its items](http://localhost:5000/catalog/JSON)
- [JSON endpoint displays all category 1 items](http://localhost:5000/catalog/1/items/JSON)

### CRUD: Read
- [Main page](http://localhost:5000/catalog/)
- [Page displays items by category](http://localhost:5000/catalog/1/items)
- [Page displays a sigle item detail](http://localhost:5000/catalog/1/1)

### CRUD: Create
- [Page with form for user to add a new item](http://localhost:5000/catalog/items/new)

### CRUD: Update
- [Page with form for user to edit an existing item](http://localhost:5000/catalog/1/7/edit)

### CRUD: Delete
- [Page for user to confirm if deleting an item](http://localhost:5000/catalog/1/7/delete)


### Authentication & Authorization
- Create, delete and update operations do consider authorization status prior to execution.
- [Google login was implemented](http://localhost:5000/login)
-  `Log in` and `Log out` button can be seen on Main page.
