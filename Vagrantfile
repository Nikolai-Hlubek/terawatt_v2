# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  config.vm.box = "centos/7"

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  config.vm.network "forwarded_port", guest: 8888, host: 8080

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  config.vm.synced_folder ".", "/vagrant", disabled: true
  
  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  config.vm.provider "virtualbox" do |vb|
    # Display the VirtualBox GUI when booting the machine
    vb.gui = true

    # Customize the amount of memory on the VM:
    vb.memory = "2048"
	# Customize the amount of cpus on the VM:
	vb.cpus = 2
  end

  # View the documentation for the provider you are using for more
  # information on available options.

  # Define a Vagrant Push strategy for pushing to Atlas. Other push strategies
  # such as FTP and Heroku are also available. See the documentation at
  # https://docs.vagrantup.com/v2/push/atlas.html for more information.
  # config.push.define "atlas" do |push|
  #   push.app = "YOUR_ATLAS_USERNAME/YOUR_APPLICATION_NAME"
  # end

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  
  # SHELL marks the end of the SHELL provisioning
  $script = <<-SHELL

	# German keyboard
	sudo localectl set-keymap de-latin1
  
    sudo yum -y update
	
	# Install prerequisites
    sudo yum groupinstall -y development
	sudo yum install -y zlib-dev openssl-devel sqlite-devel bzip2-devel wget 
	# R specific stuff
	sudo yum install -y readline-devel xz-devel libcurl-devel texinfo cairo-devel
	# R devtools
	sudo yum install -y libxml2-devel
	# R pandoc for plotly
	sudo yum install -y epel-release pandoc
	
	# Download python
	wget https://www.python.org/ftp/python/3.6.2/Python-3.6.2.tgz
	tar -xvvzf Python-3.6.2.tgz
	rm Python-3.6.2.tgz

	cd Python-3.6.2
	./configure --prefix=$HOME/usr/local
	make
	make altinstall
	cd ..
	rm -rf Python-3.6.2

	# Set path
	export PATH=$HOME/usr/local/bin:$PATH
	# Make path permanent
	echo "export PATH=$HOME/usr/local/bin:$PATH" >> .bashrc

	pip3.6 install --upgrade pip
	pip3.6 install jupyter
	pip3.6 install RISE
	jupyter-nbextension install rise --py --sys-prefix
    jupyter-nbextension enable rise --py --sys-prefix

	# Install custom notebook extensions
	pip3.6 install jupyter_contrib_nbextensions
	jupyter contrib nbextension install --user
	# Install pyton code prettifier
	pip3.6 install yapf
	jupyter nbextension enable code_prettify/code_prettify
	# Install variable inspector
	jupyter nbextension enable varInspector/main


    pip3.6 install plotly
	pip3.6 install iplantuml
	# TODO 
	# After merge of iplantuml
	# pip3 install iplantuml --jarpath .
	# wget http://sourceforge.net/projects/plantuml/files/plantuml.jar/download

	pip3.6 install numpy
	pip3.6 install scipy
	
	# Generate jupyter config (not necessary for now)
	$HOME/usr/local/bin/jupyter notebook --generate-config -y

	echo "" >> .jupyter/jupyter_notebook_config.py
	echo "## Custom additions" >> .jupyter/jupyter_notebook_config.py
	echo "c.NotebookApp.token = ''" >> .jupyter/jupyter_notebook_config.py
	echo "c.NotebookApp.password = ''" >> .jupyter/jupyter_notebook_config.py

	# Download R
	wget https://cran.uni-muenster.de/src/base/R-3/R-3.4.1.tar.gz
	tar -xvvzf R-3.4.1.tar.gz
	rm R-3.4.1.tar.gz

	cd R-3.4.1
	./configure --prefix=$HOME/usr/local --with-x=no --disable-java
	make
	make install
	cd ..
	rm -rf R-3.4.1

	# Install R packages
	$HOME/usr/local/bin/R -e "install.packages('formatR', repos = 'https://cran.uni-muenster.de', dep = TRUE)"
	$HOME/usr/local/bin/R -e "install.packages('plotly', repos = 'https://cran.uni-muenster.de', dep = TRUE)"
	$HOME/usr/local/bin/R -e "install.packages('devtools', repos = 'https://cran.uni-muenster.de', dep = TRUE)"
	$HOME/usr/local/bin/R -e "devtools::install_github('IRkernel/IRkernel')"
	# to register the kernel in the current R installation
	$HOME/usr/local/bin/R -e "IRkernel::installspec()"

	echo "## Set default 'type' for png() calls - useful when X11 device is not available!" >> .Rprofile
	echo "## NOTE: Needs 'cairo' capability" >> .Rprofile
	echo "options(bitmapType='cairo')" >> .Rprofile


	#--------------------------------------------------------------------------
	# Stuff for what-the-data hack-a-thon
	#--------------------------------------------------------------------------
	sudo yum -y groups install "GNOME Desktop" 
	# The pip version of spyder doesn't work due to some qt-webkit inconsistencies so we install from the distro
	sudo yum -y install spyder
	pip3.6 install cython
	pip3.6 install kivy
	pip3.6 install pygame
	pip3.6 install pysolar

	# install kivy for python 2.7
	sudo yum install python-pip
	sudo yum install python-devel
	sudo pip install --upgrade pip
	sudo pip install --upgrade setuptools
	sudo pip install cython
	sudo pip install kivy
	sudo pip install plyer
	sudo pip install pygame
	
	# Git
	sudo yum -y install git

	mkdir -p what-the-data
	git clone https://github.com/nikolai-hlubek/terawatt /home/vagrant/what-the-data
	# Private repository, would need credentials
	#git clone https://github.com/nikolai-hlubek/terawatt_v2 /home/vagrant/what-the-data_v2
    
	# remove inital folder structure
	rm -rf Desktop
	rm -rf Documents
	rm -rf Downloads
	rm -rf Music
	rm -rf Pictures
	rm -rf Public
	rm -rf Templates
	rm -rf Videos
	#--------------------------------------------------------------------------
	
	SHELL

	config.vm.provision "shell", privileged: false, inline: $script
	
    config.vm.provision "shell", 
		inline: "nohup $HOME/usr/local/bin/jupyter-notebook --ip 0.0.0.0 --port 8888 --notebook-dir=$HOME --no-browser &",
		privileged: false,
		run: "always"
	end


#Known Issues
#
#The VirtualBox Guest Additions are not preinstalled; if you need them for shared folders, please install the vagrant-vbguest plugin. We recommend using NFS instead of VirtualBox shared folders if possible.
#Since the Guest Additions are missing, our images are preconfigured to use rsync for synced folders. Windows users can either use SMB for synced folders, or disable the sync directory by adding the line config.vm.synced_folder ".", "/vagrant", disabled: true to the Vagrantfile.
#Vagrant 1.8.5 is unable to create new Linux boxes due to Vagrant bug #7610. You can use Vagrant 1.8.4 until version 1.8.6 is released.
