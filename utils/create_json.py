from pathlib import Path
import json
repo=Path('./MINGW-packages')
save_dir=Path('./packages')
save_dir.mkdir(exist_ok=True)
print(repo.absolute())

for i in repo.iterdir():
    main={'type':'pypi',"repo":"MINGW"}
    if i.is_dir() and "python-" in str(i):
        if not i.glob('*.patch'):
            continue
        project = i.stem[17:]  #mingw-w64-python- = 17 chars :)
        main['project'] = project
        main['name']=i.stem
        with open(save_dir/(str(i.stem)+'.json'),'w') as f:
            json.dump(main,f,indent=4)
        del main
