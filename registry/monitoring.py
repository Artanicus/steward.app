import prometheus_client
from python_grpc_prometheus.prometheus_server_interceptor import PromServerInterceptor

psi = PromServerInterceptor()
prometheus_client.start_http_server(8000)
