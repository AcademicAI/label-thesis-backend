# Quickstart


1. Instale o label-studio
    ```sh
    pip install label-studio==1.8.1
    ```

2. Inicie a aplicação do label studio, em seguida acesse suas configurações clicando no canto superior direito em `Account & Settings` para copiar o token de acesso.
    ```sh
    label-studio start
    ```
3. Crie o arquivo `.env` a partir do `.env.sample`
    ```sh
    cp .env.sample .env
    ```
4. Edite o arquivo `.env` com o endereço do label-studio, informando o hostname¹ da sua aplicação e o token de acesso:
    ```
    LABEL_STUDIO_HOST=http://<hostname>:<porta>
    API_KEY=seu token aqui
    ```
    ¹Use `cat /proc/sys/kernel/hostname` para obter o hostname caso esteja executando localmente.

5. Execute a aplicação

    ```sh
    docker compose -up
    ```
6. No label-studio, nas configurações do projeto adicione a url da aplicação
    ```
    http://<hostname>:9090
    ```