import json
import os
import re 
from .models import *
from .serializers import *
from .views import get_request_body , good_response , bad_response , clean_phone_number
from typing import Any
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
# customer modules
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.db import IntegrityError
from django.db.models import Q
from django.utils.text import slugify
from django.core.files.storage import default_storage
from django.middleware.csrf import get_token
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.core.mail import send_mail
# Pro modules
import os
import json
import re
from .models import *
from userEx.views import *
from userEx.models import *
from userEx.serializers import *
from datetime import datetime
from django.db.models import Avg
from django.conf import settings
from django.db.models import Q
from django.db.models import Prefetch
from django.utils.text import slugify
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.middleware.csrf import get_token
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator