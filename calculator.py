import streamlit as st

def calculate_ostore_capacity(servers_per_rack, drives_per_server, drive_capacity, stripe_size, parity_shards):
    total_drives = servers_per_rack * drives_per_server

    if total_drives < stripe_size:
        return {
            "error": f"{stripe_size} or more drives required"
        }

    raw_capacity = total_drives * drive_capacity

    # Calculate usable capacity
    data_shards = stripe_size - parity_shards
    usable_capacity = (data_shards / stripe_size) * raw_capacity

    storage_efficiency = usable_capacity / raw_capacity

    if total_drives % stripe_size != 0: 
        return {
            "error": f"Total drives: {total_drives} i.e {servers_per_rack} x {drives_per_server} have to be a multiple of the stripe size"
        }

    no_of_diskset = total_drives / stripe_size

    if servers_per_rack % stripe_size == 0:
        node_set = servers_per_rack / stripe_size 
        server_failure_tolerance = parity_shards * node_set
    elif servers_per_rack % 3 == 0 and drives_per_server % stripe_size == 0:
        server_failure_tolerance = servers_per_rack / 3 
    else: 
        no_of_nodes_per_disket = servers_per_rack / no_of_diskset
        no_of_drives_per_server_per_diskset  = stripe_size / no_of_nodes_per_disket
        server_failure_tolerance = no_of_diskset * (parity_shards // no_of_drives_per_server_per_diskset)

    drive_failure_tolerance_total = parity_shards * no_of_diskset
    drive_failure_tolerance_per_stripe = parity_shards

    # if servers_per_rack < stripe_size: 
    #     if stripe_size % servers_per_rack != 0: 
    #         server_failure_tolerance = 0
    #     else: 
    #         no_of_drives_per_server_per_diskset = stripe_size / servers_per_rack
    #         if no_of_drives_per_server_per_diskset == parity_shards: 
    #             server_failure_tolerance = parity_shards * no_of_diskset
    #         else: 
    #             server_failure_tolerance = 0
    # else: 
    #     if servers_per_rack % stripe_size !=0: 


    # if servers_per_rack % stripe_size != 0: 
    #     server_failure_tolerance = 0 
    # else: 



    # total_servers = servers_per_rack
    # if total_servers >= stripe_size:
    #     server_failure_tolerance = parity_shards
    # else:
    #     stripes_per_server = [0] * total_servers
    #     for i in range(stripe_size):
    #         stripes_per_server[i % total_servers] += 1

    #     max_server_failures = 0
    #     failed_shards = 0 
    #     for stripes in stripes_per_server:
    #         if stripes <= parity_shards:
    #             failed_shards += stripes
    #             if failed_shards <= parity_shards: 
    #                 max_server_failures += 1

    #     server_failure_tolerance = max_server_failures

    return {
        "Usable Capacity": usable_capacity,
        "Raw Capacity": raw_capacity,
        "Storage Efficiency": storage_efficiency,
        "Drive Failure(s) Tolerance Total": drive_failure_tolerance_total,
        "Drive Failure(s) Tolerance Per Stripe": drive_failure_tolerance_per_stripe,
        "Server Failure(s) Tolerance": server_failure_tolerance
    }

def main():
    st.title("Ostore Erasure Code Calculator")

    # Input fields
    servers_per_rack = st.number_input("Number of Servers", min_value=1, value=4)
    drives_per_server = st.number_input("Number of Drives per Server", min_value=1, value=8)
    drive_capacity = st.number_input("Drive Capacity (TiB)", min_value=1, value=12)

    total_drives = servers_per_rack * drives_per_server

    stripe_size_options = [6, 9]
    stripe_size = st.selectbox("Erasure Code Stripe Size (K+M)", stripe_size_options)

    if stripe_size == 6:
        parity_shards = 2
    elif stripe_size == 9:
        parity_shards = 3

    st.write(f"Erasure Code Parity (M): {parity_shards}")

    if st.button("Calculate"):
        results = calculate_ostore_capacity(servers_per_rack, drives_per_server, drive_capacity * 1024, stripe_size, parity_shards)

        if "error" in results:
            st.write(f"**Error:** {results['error']}")
        else:
            st.write(f"**Usable Capacity:** {results['Usable Capacity'] / 1024:.2f} TiB")
            st.write(f"**Raw Capacity:** {results['Raw Capacity'] / 1024:.2f} TiB")
            st.write(f"**Storage Efficiency:** {results['Storage Efficiency'] * 100:.0f}%")
            st.write(f"**Drive Failure(s) Tolerance:** {results['Drive Failure(s) Tolerance Total']} drives in total ({results['Drive Failure(s) Tolerance Per Stripe']} out of {stripe_size} drives per stripe)")
            st.write(f"**Server Failure(s) Tolerance:** {results['Server Failure(s) Tolerance']} server(s) in total ({results['Server Failure(s) Tolerance']} out of {servers_per_rack} servers per stripe)")

if __name__ == "__main__":
    main()
