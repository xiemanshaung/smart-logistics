# Windows PowerShell 检查数据库命令

## 检查 PostgreSQL 容器是否运行

### 方法一：使用过滤器（推荐）
```powershell
docker ps --filter "name=postgres"
```

### 方法二：查看所有容器
```powershell
docker ps
```

### 方法三：查看容器日志
```powershell
docker logs dreo-postgres
```

### 方法四：检查容器健康状态
```powershell
docker inspect dreo-postgres --format='{{.State.Health.Status}}'
```

## 常用 Docker 命令（Windows PowerShell）

```powershell
# 启动数据库
docker-compose up -d postgres

# 停止数据库
docker-compose stop postgres

# 重启数据库
docker-compose restart postgres

# 查看数据库日志
docker logs -f dreo-postgres

# 进入数据库容器（如果需要）
docker exec -it dreo-postgres psql -U dreo_user -d dreo_logistics

# 测试数据库连接（在容器内）
docker exec dreo-postgres pg_isready -U dreo_user -d dreo_logistics
```

## 注意

Windows PowerShell 不支持 Linux 命令如 `grep`，请使用：
- `docker ps --filter` 替代 `docker ps | grep`
- `Select-String` 替代 `grep`（如果必须使用管道）

