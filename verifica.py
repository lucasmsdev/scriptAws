import boto3
from botocore.exceptions import ClientError

# Lista de serviços, seus nomes personalizados e suas tags
services = [
    {'service_name': 'ec2', 'tags': {'Name': 'Environment', 'Environment': 'Production'}},
    {'service_name': 's3', 'tags': {'Name': 'bucket-teste-andershow', 'Environment': 'Production'}},
    # Adicione mais serviços, nomes personalizados e suas tags conforme necessário
]

# Função para verificar se os serviços estão funcionando e pontuar com base nos acertos
def check_services(aws_access_key_id, aws_secret_access_key, aws_session_token):
    total_score = 0
    for service_data in services:
        service = service_data['service_name']
        score = 0  # Pontuação para este serviço
        try:
            # Conexão com o serviço AWS usando Boto3
            client = boto3.client(
                service,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token,
                region_name='us-east-1'  # Altere a região conforme necessário
            )

            # Verificando se o serviço está ativo
            if service == 'ec2':
                running_instances = client.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])['Reservations']
                if running_instances:
                    print("Existem instâncias EC2 em execução.")
                    score += 1  # Adiciona um ponto se o serviço estiver ativo

                    # Verifica se as tags estão presentes para cada instância EC2
                    for reservation in running_instances:
                        for instance in reservation['Instances']:
                            instance_tags = instance.get('Tags', [])
                            for tag_key, tag_value in service_data['tags'].items():
                                if any(tag['Key'] == tag_key and tag['Value'] == tag_value for tag in instance_tags):
                                    print(f"A tag '{tag_key}' com valor '{tag_value}' está presente na instância EC2.")
                                    score += 1  # Adiciona um ponto para cada tag correta encontrada

            elif service == 's3':
                buckets = client.list_buckets()['Buckets']
                if buckets:
                    print("Existem buckets S3 disponíveis.")
                    score += 1  # Adiciona um ponto se o serviço estiver ativo

                    # Verifica se as tags estão presentes para cada bucket S3
                    for bucket in buckets:
                        bucket_name = bucket['Name']
                        response = client.get_bucket_tagging(Bucket=bucket_name)
                        bucket_tags = response.get('TagSet', [])
                        for tag_key, tag_value in service_data['tags'].items():
                            if any(tag['Key'] == tag_key and tag['Value'] == tag_value for tag in bucket_tags):
                                print(f"A tag '{tag_key}' com valor '{tag_value}' está presente no bucket S3 '{bucket_name}'.")
                                score += 1  # Adiciona um ponto para cada tag correta encontrada
        
        except Exception as e:
            print(f"Erro ao acessar o serviço {service}: {str(e)}")
        
        total_score += score  # Adiciona a pontuação deste serviço à pontuação total
    
    print(f"Pontuação total: {total_score}")

# Obtendo credenciais da AWS do usuário
aws_access_key_id = input("Insira sua AWS Access Key ID: ")
aws_secret_access_key = input("Insira sua AWS Secret Access Key: ")
aws_session_token = input("Insira seu AWS Session Token (se aplicável): ")

# Executando a função de verificação
check_services(aws_access_key_id, aws_secret_access_key, aws_session_token)
