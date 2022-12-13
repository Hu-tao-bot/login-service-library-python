import setuptools

setuptools.setup(
	name="hutao-login-gateway",
	version="1.0.1",
	author="Hu Tao Bot",
	author_email="dev@m307.dev",
	description="Hu Tao Login Gateway server",
	url="https://github.com/Hu-tao-bot/login-service-library",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	install_requires=[
		"pydantic",
		"python-socketio[asyncio_client]"
	],
	python_requires=">=3.6",
	include_package_data=True
)