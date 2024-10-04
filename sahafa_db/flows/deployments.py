import sahafa_db.flows.test_flow as test_flow
from prefect import flow

if __name__ == "__main__":
    
     # add schedule in a cron string   
    flow(
        name="recording-flow",
        work_pool_name="default-work-pool",
        flow_location="recording_flow",
        parameters={"repos": ["PrefectHQ/Prefect"]},
        cron="0 0 * * *"
    )
