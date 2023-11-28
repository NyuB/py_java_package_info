# Check and generate package-info.java

## Usage

### Generation

#### All
**set-all** : replace already present and generate missing package info from template

`python3 package-info.py set-all <sources-root> <template-file>`

```bash
$> python3 package-info.py set-all src/main/java my-template.txt
```

#### Only missing
**set-missing** : only generate missing package info from template

`python3 package-info.py set-all <sources-root> <template-file>`

```bash
$> python3 package-info.py set-missing src/test/kotlin template.txt
```

### Check
**check** : exit with error code 1 if some package-info.java are missing

`python3 package-info.py check <sources-root>`

```bash
python3 package-info.py check src/main.java
```