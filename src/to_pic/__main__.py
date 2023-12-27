'''
Author: Abel
Date: 2023-12-27 10:05:16
LastEditTime: 2023-12-27 10:05:16
'''
import uvicorn
from .app import app

def main():
    uvicorn.run(app, host='0.0.0.0', port=19527)

if __name__ == '__main__':
    main()
