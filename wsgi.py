from server import app
import os
import argparse
os.environ["ENV_SETTINGS"]="PROD"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='find env settings',prog='server.py')
    parser.add_argument('--env',dest='ENV_SETTINGS',default='PROD',help="Setup the enviroment",choices=["DEV","PROD"])

    arg = (parser.parse_args())
    env_settings = (arg.ENV_SETTINGS)
    if os.environ.get("ENV_SETTINGS",-1) ==-1:
        os.environ['ENV_SETTINGS']=env_settings
    print("Booting the server in ",os.environ['ENV_SETTINGS']," settings")
    app.run()