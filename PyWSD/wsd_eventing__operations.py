#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import wsd_common


# TODO: support both supported time formats, and/or hide format to user by using language facilities


def wsd_subscribe(hosted_service, event_uri, notify_addr, expiration=None):
    """
    Subscribe to a certain type of events of a wsd service

    :param hosted_service: the wsd service to receive event notifications from
    :param event_uri: the full URI of the targeted event class. \
                    Those URIs are taken from ws specifications
    :param notify_addr: The address to send notifications to.
    :param expiration: Expiration time, as a string in the following form: P*Y**M**DT**H**M**S
    :return: the xml SubscribeResponse of the wsd service\
             or False if a fault message is received instead
    """

    expiration_tag = "<wse:Expires>%s</wse:Expires>" % expiration if expiration is not None else ""

    fields_map = {"FROM": wsd_common.urn,
                  "TO": hosted_service.ep_ref_addr,
                  "NOTIFY_ADDR": notify_addr,
                  "EXPIRES": expiration,
                  "FILTER_DIALECT": "http://schemas.xmlsoap.org/ws/2006/02/devprof/Action",
                  "EVENT": event_uri,
                  "OPT_EXPIRATION": expiration_tag}
    x = wsd_common.submit_request(hosted_service.ep_ref_addr,
                                  "ws-eventing__subscribe.xml",
                                  fields_map)

    if x is False or wsd_common.check_fault(x):
        return False

    return wsd_common.xml_find(x, ".//wse:SubscribeResponse")


def wsd_unsubscribe(hosted_service, subscription_id):
    """
    Unsubscribe from events notifications of a wsd service

    :param hosted_service: the wsd service from which you want to unsubscribe for events
    :param subscription_id: the ID returned from a previous successful event subscription call
    :return: False if a fault message is received instead, True otherwise
    """
    fields_map = {"FROM": wsd_common.urn,
                  "TO": hosted_service.ep_ref_addr,
                  "SUBSCRIPTION_ID": subscription_id}
    x = wsd_common.submit_request(hosted_service.ep_ref_addr,
                                  "ws-eventing__unsubscribe.xml",
                                  fields_map)

    return False if x is False or wsd_common.check_fault(x) else True


def wsd_renew(hosted_service, subscription_id, expiration):
    """
    Renew an events subscription of a wsd service

    :param hosted_service: the wsd service that you want to renew the subscription
    :param subscription_id: the ID returned from a previous successful event subscription call
    :param expiration: Expiration time, as a string in the following form: P*Y**M**DT**H**M**S
    :return: False if a fault message is received instead, True otherwise
    """

    fields_map = {"FROM": wsd_common.urn,
                  "TO": hosted_service.ep_ref_addr,
                  "SUBSCRIPTION_ID": subscription_id,
                  "EXPIRES": expiration}
    x = wsd_common.submit_request(hosted_service.ep_ref_addr,
                                  "ws-eventing__renew.xml",
                                  fields_map)

    return False if x is False or wsd_common.check_fault(x) else True


def wsd_get_status(hosted_service, subscription_id):
    """
    Get the status of an events subscription of a wsd service

    :param hosted_service: the wsd service from which you want to hear about the subscription status
    :param subscription_id: the ID returned from a previous successful event subscription call
    :return: False if a fault message is received instead, \
             none if the subscription has no expiration set, \
             the expiration date otherwise
    """
    fields_map = {"FROM": wsd_common.urn,
                  "TO": hosted_service.ep_ref_addr,
                  "SUBSCRIPTION_ID": subscription_id}
    x = wsd_common.submit_request(hosted_service.ep_ref_addr,
                                  "ws-eventing__get_status.xml",
                                  fields_map)

    if x is False or wsd_common.check_fault(x):
        return False
    e = wsd_common.xml_find(x, ".//wse:Expires")
    return e.text if e is not None else None


def __demo():
    import wsd_scan__events
    import wsd_transfer__operations
    import wsd_discovery__operations

    wsd_common.init()
    tsl = wsd_discovery__operations.get_devices()
    for a in tsl:
        res = wsd_transfer__operations.wsd_get(a)
        if res is not False:
            (ti, hss) = res
            for b in hss:
                if "wscn:ScannerServiceType" in b.types:
                    listen_addr = "http://192.168.1.109:6666/wsd"
                    h = wsd_scan__events.wsd_scanner_all_events_subscribe(b, listen_addr, "P0Y0M0DT30H0M0S")
                    # wsd_renew(b, h)
                    wsd_get_status(b, h)
                    wsd_unsubscribe(b, h)


if __name__ == "__main__":
    __demo()