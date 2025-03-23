import asyncio
import logging

from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .agents.chat_agent import ForexChatAgent

# 获取logger实例
logger = logging.getLogger("django")

# Create your views here.


@method_decorator(csrf_exempt, name="dispatch")
class ChatView(APIView):
    permission_classes = [AllowAny]  # 暂时允许所有请求，不需要认证

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = ForexChatAgent()

    def post(self, request):
        try:
            message = request.data.get("message")
            use_deep_search = request.data.get("useDeepSearch", False)
            
            if not message:
                return Response(
                    {"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            response = asyncio.run(self.agent.chat(message, use_deep_search=use_deep_search))
            return Response({"response": response})
        except Exception as e:
            logger.error(f"Chat error: {str(e)}", exc_info=True)  # 记录详细错误日志
            return Response(
                {"error": "Internal server error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
