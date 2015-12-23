
from pyactive.controller import init_host, serve_forever, start_controller, interval, sleep
from pyactive.exception import TimeoutError, PyactiveError
import requests
import operator
import json
import redis
import logging

mappings = {'>': operator.gt, '>=': operator.ge,
        '==': operator.eq, '<=': operator.le, '<': operator.lt,
        '!=':operator.ne, "OR":operator.or_, "AND":operator.and_}

#TODO: Add the redis connection into rule object
r = redis.StrictRedis(host='localhost', port=6379, db=0)
logging.basicConfig(filename='./rule.log', format='%(asctime)s %(message)s', level=logging.INFO)


class Rule(object):
    """
    Rule: Each policy of each tenant is compiled as Rule. Rule is an Actor and it will be subscribed
    in the workloads metrics. When the data received from the workloads metrics satisfies
    the conditions defined in the policy,the Rule actor executes an Action that it is
    also defined in the policy.
    """
    _sync = {'get_tenant':'2'}
    _async = ['update', 'start_rule', 'stop_actor']
    _ref = []
    _parallel = []

    def __init__(self, rule_parsed, tenant, host, host_ip, host_port, host_transport):
        """
        Inicialize all the variables needed for the rule.

        :param rule_parsed: The rule parsed by the dsl_parser.
        :type rule_parsed: **any** PyParsing type
        :param tenant: The tenant id assigned to this rule.
        :type tenant_info: **any** String type
        :param host: The proxy host provided by the PyActive Middleware.
        :type host: **any** PyActive Proxy type
        :param host_ip: The host ip adress.
        :type host_ip: **any** String type
        :param host_port: The host port address.
        :type host_port: **any** Numeric type.
        :param host_transport: The host transport used for the comunication.
        :type host_transport: **any** String type.

        """
        logging.info('Rule init: OK')
        logging.info('Rule: %s', rule_parsed.asList())
        self.rule_parsed = rule_parsed
        self.tenant = tenant
        self.conditions = rule_parsed.condition_list.asList()
        self.observers_values = {}
        self.observers_proxies = {}
        self.base_uri = host_transport+'://'+host_ip+':'+str(host_port)+'/'
        tcpconf = (host_transport,(host_ip, host_port))
        self.host = host
        self.action_list = rule_parsed.action_list

    def stop_actor(self):
        """
        Method called to end the rule. This method unsubscribes the rule from all the workload metrics subscribed, and
        kills the actor of the rule.
        """
        for observer in self.observers_proxies.values():
            observer.detach(self.proxy)
        r.hset("policy:"+str(self.id), "alive", False)
        self._atom.stop()

    def start_rule(self):
        """
        Method called afeter init to start the rule. Basically this method allows to be called remotelly and calls the
        internal method **check_metrics()** which subscribes the rule to all the workload metrics necessaries.
        """
        print 'Start rule'
        self.check_metrics(self.conditions)


    def add_metric(self, workload_name):
        """
        The add_metric method subscribes the rule to all workload metrics that it
        needs to check the conditions defined in the policy

        :param workload_name: The name that identifies the workload metric.
        :type workload_name: **any** String type

        """
        if value not in self.observers_values.keys():
            #Subscrive to metric observer
            print 'hola add metric', self.base_uri+'metrics.'+workload_name+'/'+workload_name.title()+'/'+workload_name
            observer = self.host.lookup(self.base_uri+'metrics.'+workload_name+'/'+workload_name.title()+'/'+workload_name)
            observer.attach(self.proxy)
            self.observers_proxies[workload_name] = observer
            self.observers_values[workload_name] = None


    def check_metrics(self, condition_list):
        """
        The check_metrics method finds in the condition list all the metrics that it
        needs to check the conditions, when find some metric that it needs, call the
        method add_metric.

        :param condition_list: The list of all the conditions.
        :type condition_list: **any** List type
        """
        if not isinstance(condition_list[0], list):
            self.add_metric(condition_list[0].lower())
        else:
            for element in condition_list:
                if element is not "OR" and element is not "AND":
                    self.check_metrics(element)

    def update(self, metric, tenant_info):
        """
        The method update is called by the workloads metrics following the observer
        pattern. This method is called to send to this actor the data updated.

        :param metric: The name that identifies the workload metric.
        :type metric: **any** String type

        :param tenant_info: Contains the timestamp and the value sent from workload metric.
        :type tenant_info: **any** PyParsing type
        """
        print 'Success update:  ', tenant_info

        self.observers_values[metric]=tenant_info.value
        #TODO Check the last time updated the value
        #Check the condition of the policy if all values are setted. If the condition
        #result is true, it calls the method do_action
        if all(val!=None for val in self.observers_values.values()):
            if self.check_conditions(self.conditions):
                print self.do_action()
        else:
            print 'not all values setted', self.observers_values.values()

    def check_conditions(self, condition_list):
        """
        The method **check_conditions()** runs the ternary tree of conditions to check if the
        **self.observers_values** complies the conditions. If the values comply the conditions return
        True, else return False.

        :param condition_list: A list of all the conditions
        :type condition_list: **any** List type

        :return: If the values comply the conditions
        :rtype: boolean type.
        """
        if not isinstance(condition_list[0], list):
            result = mappings[condition_list[1]](float(self.observers_values[condition_list[0].lower()]), float(condition_list[2]))
        else:
            result = self.check_conditions(condition_list[0])
            for i in range(1, len(condition_list)-1, 2):
                result = mappings[condition_list[i]](result, self.check_conditions(condition_list[i+1]))
        return result

    def get_tenant(self):
        """
        Retrun the tenant assigned to this rule.

        :return: Return the tenant id assigned to this rule
        :rtype: String type.
        """
        return self.tenant


    def do_action(self):
        """
        The do_action method is called after the conditions are satisfied. So this method
        is responsible to execute the action defined in the policy.
        """
        #TODO: Handle the token generation. Auto-login when this token expires. Take credentials from config file.
        headers = {"X-Auth-Token":"c2633386b09a461a806845a100facbf0"}
        dynamic_filter = r.hgetall("filter:"+str(self.action_list.filter))

        if self.action_list.action == "SET":

            #TODO Review if this tenant has already deployed this filter. Not deploy the same filter more than one time.

            url = dynamic_filter["activation_url"]+"/"+self.tenant+"/deploy/"+str(dynamic_filter["identifier"])
            print 'params: ', self.action_list.params
            response = requests.put(url, json.dumps(self.action_list.params), headers=headers)

            if 200 > response.status_code >= 300:
                print 'ERROR RESPONSE'
            else:
                print response.text, response.status_code
                self.stop_actor()
                return response.text

        elif self.action_list.action == "DELETE":

            url = dynamic_filter["activation_url"]+"/"+self.tenant+"/undeploy/"+str(dynamic_filter["identifier"])
            response = requests.put(url, json.dumps(self.action_list.params), headers=headers)

            if 200 > response.status_code >= 300:
                print 'ERROR RESPONSE'
            else:
                print response.text, response.status_code
                self.stop_actor()
                return response.text

        return 'Not action supported'
