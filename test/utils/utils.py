import base64
import json
from pathlib import Path

def lambda_payload_builder(data: dict, funcname: str, outputfname: str):
    s = json.dumps(data)
    print(s)
    s_encoded = base64.b64encode(s.encode('utf-8')).decode('utf-8')
    output_payload = \
        { "Records" : 
            [ 
                { 
                    "kinesis" : 
                        {
                            "data" :
                                s_encoded
                        }
                }
            ]
        }

    output_path = Path(__file__).resolve().parent.parent\
        .joinpath('functions')\
            .joinpath(funcname)\
                .joinpath('data')\
                    .joinpath(outputfname)

    with open(output_path,'w') as outfile:
        outfile.write(json.dumps(output_payload))

    print(f'data written to {output_path}')


if __name__ == "__main__":      
    print('main')  
    data = {"msg":"hi"}
    funcname='aroundTheWorld'
    outputfname='hello.json'    
    lambda_payload_builder(data=data, funcname=funcname,outputfname=outputfname)
